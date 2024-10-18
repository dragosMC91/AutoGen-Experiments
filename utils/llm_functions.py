from utils.http_utils import (
    get_dad_jokes,
    get_arxiv_article_content,
    get_latest_arxiv_papers,
)

class Functions:
    get_dad_jokes = {
        "name": "get_dad_jokes",
        "f": get_dad_jokes,
        "description": "Fetches a list of dad jokes based on a search term. Allows pagination with page and limit parameters.",
    }

    get_arxiv_article_content = {
        "name": "get_arxiv_article_content",
        "f": get_arxiv_article_content,
        "description": "Fetches the abstract or full text of a research paper from an arXiv article given its URL.",
    }

    get_latest_arxiv_papers = {
        "name": "get_latest_arxiv_papers",
        "f": get_latest_arxiv_papers,
        "description": """Fetch the latest arXiv papers within a given time interval and category.
Args: submit_interval (str, optional): Time interval for paper submission in the format
'YYYYMMDDHHMMSS TO YYYYMMDDHHMMSS'. If None, defaults to previous day interval.
category (str): The arXiv category to search for. Defaults to 'cs.AI' for the topic of AI.
max_results (int): Maximum number of results to return. Defaults to 300.
Returns: List[Dict[str, str]]: A list of dictionaries containing paper titles and IDs.""",
    }
