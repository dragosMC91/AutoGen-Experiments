import requests
import arxiv
import re
import time
from typing import Dict, Optional, List, Union
from io import BytesIO
from pypdf import PdfReader
from datetime import datetime, timedelta
from requests.exceptions import ConnectionError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RATE_LIMIT = 3  # seconds
last_call_time = 0
DEFAULT_DATE_FORMAT = "%Y%m%d"
START_DAY_HHMM = "0000"
DEFAULT_CATEGORY = "cs.AI"
DEFAULT_MAX_RESULTS = 300


def get_formatted_date(
    days_offset: int = 0, date_format: str = DEFAULT_DATE_FORMAT
) -> str:
    """Get a formatted date string with an optional offset from the current
    date.

    Args:
        days_offset (int): Number of days to offset from the current date. Defaults to 0.
        date_format (str): The desired date format. Defaults to 'yyyyMMDD'.

    Returns:
        str: The formatted date string.

    Example:
        >>> get_formatted_date(-1)
        '20230509'  # Assuming current date is 2023-05-10
        >>> get_formatted_date(1, "%Y-%m-%d")
        '2023-05-11'  # Assuming current date is 2023-05-10
    """
    current_date = datetime.now()
    offset_date = current_date + timedelta(days=days_offset)
    return offset_date.strftime(date_format)


def get_latest_arxiv_papers(
    submit_interval: Optional[str] = None,
    category: str = DEFAULT_CATEGORY,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> List[Dict[str, str]]:
    """Fetch the latest arXiv papers within a given time interval and category.

    Args:
        submit_interval (str, optional): Time interval for paper submission in the format
            'YYYYMMDDHHMMSS TO YYYYMMDDHHMMSS'. If None, defaults to previous day interval.
        category (str): The arXiv category to search for. Defaults to 'cs.AI' for the topic of AI.
        max_results (int): Maximum number of results to return. Defaults to 300.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing paper titles and IDs.

    Raises:
        arxiv.arxiv.HTTPError: If there's an error with the arXiv API request.

    Example:
        >>> papers = get_latest_arxiv_papers(category="physics.gen-ph", max_results=2)
        >>> papers
        [
            {'title': 'Example Paper 1', 'id': '2305.12345'},
            {'title': 'Example Paper 2', 'id': '2305.67890'},
        ]
    """
    if submit_interval is None:
        yesterday = get_formatted_date(-1)
        today = get_formatted_date()
        submit_interval = f"{yesterday}{START_DAY_HHMM} TO {today}{START_DAY_HHMM}"

    query = f'all:{category} AND submittedDate:[{submit_interval}]'
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate
    )

    try:
        results = list(client.results(search))
    except arxiv.arxiv.HTTPError as e:
        print(f"Error fetching results from arXiv API: {e}")
        return []

    # TODO include summary in results and pass results to a small/cheap middleman LLM for extra summarization
    return [{"title": result.title, "id": result.get_short_id()} for result in results]


def extract_pdf_text_content(
    pdf_content: Union[bytes, BytesIO],
):
    """Extract text content from a PDF.

    Args:
        pdf_content (Union[bytes, BytesIO]): The PDF content as bytes or BytesIO object.

    Returns:
        str: The extracted text content from the PDF.

    Raises:
        Exception: For any errors during PDF processing.
    """
    try:
        if isinstance(pdf_content, bytes):
            pdf_content = BytesIO(pdf_content)

        pdf = PdfReader(pdf_content)
        return ''.join(map((lambda page: page.extract_text()), pdf.pages))
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def strip_references(paper_text: str) -> str:
    """Strip the references section from a research paper text.

    Args:
        paper_text (str): The full text of the research paper.

    Returns:
        str: The paper text with the references section removed.
    """
    # Common headers for the references section
    reference_headers = [
        r'\bReferences\b',
        r'\bBibliography\b',
        r'\bWorks Cited\b',
        r'\bLiterature Cited\b',
        r'\bCited Literature\b',
    ]

    pattern = '|'.join(reference_headers)

    # Find the position of the references section
    match = re.search(pattern, paper_text, re.IGNORECASE)

    if match:
        # If found, return the text up to the start of the references section
        return paper_text[: match.start()].strip()
    else:
        # If no references section is found, return the original text
        return paper_text.strip()


def get_arxiv_article_content(arxiv_ref: str, fetch_only_abstract: bool = False) -> str:
    """Fetches the abstract or full text of a research paper from an arXiv
    article given its URL|id.

    Args:
        arxiv_ref (str): The URL of the arXiv article (abstract | PDF | id).
        fetch_only_abstract (bool, optional): When True only fetch the abstract not the entire article text. Defaults to False.

    Returns:
        str: A string containing either the abstract or full text of the article.
        If either is not available, the corresponding value will be None.

    Raises:
        ValueError: If the provided URL is invalid or the arXiv ID cannot be extracted.
    """
    global last_call_time

    try:
        # Rate limiting
        current_time = time.time()
        if current_time - last_call_time < RATE_LIMIT:
            time.sleep(RATE_LIMIT - (current_time - last_call_time))
        last_call_time = time.time()

        logger.info(f"Fetching content for URL: {arxiv_ref}")

        # Extract arXiv ID from the ref
        arxiv_id_match = re.search(
            r'(?:arxiv.org(?:/abs|/pdf)?/)?(\d+\.\d+)(?:v\d)?', arxiv_ref
        )
        if not arxiv_id_match:
            raise ValueError("Invalid arXiv URL. Unable to extract arXiv ID.")

        arxiv_id = arxiv_id_match.group(1)
        logger.info(f"Extracted arXiv ID: {arxiv_id}")

        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(client.results(search))
        if not results:
            logger.error("No results found for the given arXiv ID.")
            return None, None

        result = results[0]
        content = result.summary

        if fetch_only_abstract is False:
            try:
                pdf_url = result.pdf_url
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    content = strip_references(
                        extract_pdf_text_content(response.content)
                    )
                    logger.info("Successfully downloaded PDF content")
                else:
                    logger.warning(
                        f"Failed to download PDF. Status code: {response.status_code}"
                    )
            except Exception as e:
                logger.error(f"Unable to download full text: {str(e)}")

        return content

    except arxiv.arxiv.HTTPError as e:
        logger.error(f"Error accessing arXiv API: {str(e)}")
        return None, None
    except arxiv.arxiv.UnexpectedEmptyPageError:
        logger.error("Error: No results found for the given arXiv ID.")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return None, None


def get_dad_jokes(search_term: str, page: int = 1, limit: int = 10) -> str:
    """Fetches a list of dad jokes based on a search term.

    Parameters:
    - search_term: The search term to find jokes about.
    - page: The page number of results to fetch (default is 1).
    - limit: The number of results to return per page (default is 20, max is 30).

    Returns:
    A list of dad jokes.
    """
    print("calling function with", search_term, limit, page)
    url = "https://icanhazdadjoke.com/search"
    headers = {"Accept": "application/json"}
    params = {"term": search_term, "page": page, "limit": limit}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        jokes = [joke["joke"] for joke in data["results"]]
        return jokes
    else:
        return f"Failed to fetch jokes, status code: {response.status_code}"


def is_litellm_server_running():
    path = '/routes'

    try:
        response = requests.get(url=f'http://localhost:30000{path}')
    except ConnectionError:
        print(
            "\nLiteLLM server is not started. If you want to monitor costs, make sure to boot it up.\n"
        )
        return False

    if response.status_code != 200:
        print("LiteLLM server was not started correctly")
        return False

    try:
        data = response.json()
    except ValueError:
        print(
            f"The response of the {path} request is not a valid JSON. LiteLLM might not be started correctly."
        )
        return False

    if 'routes' not in data or not isinstance(data['routes'], list):
        print(
            f"Failed to validate {path} response: it does not contain a 'routes' key or it's not a list."
        )
        return False

    return True
