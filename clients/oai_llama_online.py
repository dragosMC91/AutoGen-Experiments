from typing import Union, Protocol, runtime_checkable, Optional
from autogen.oai.client import OpenAIClient
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.completion import Completion
from openai import OpenAI
import inspect
from pydantic import BaseModel


@runtime_checkable
class FormatterProtocol(Protocol):
    def format(self) -> str:
        ...


class CitationEnabledOpenAIClient(OpenAIClient):
    """An OpenAI client wrapper with citation support.

    Some models provide extra args in responses like perplexity's ollama model which adds an extra 'citations' key.
    Since we are using LiteLLM to translate responses into OpenAI responses we just need to override message_retrieval
    from OpenAIClient and not write a client class from the ground up.
    Call stack ConversableAgent.generate_oai_reply -> _generate_oai_reply_from_client -> extracted_response = llm_client.extract_text_or_completion_object(response)[0] -> (oai/client.py.extract_text_or_completion_object -> message_retrieval_function -> message_retrieval)
    """

    def __init__(self, config, response_format: Optional[BaseModel] = None):
        openai_kwargs = set(inspect.getfullargspec(OpenAI.__init__).kwonlyargs)
        openai_config = {**{k: v for k, v in config.items() if k in openai_kwargs}}
        client = OpenAI(**openai_config)
        self._oai_client = client
        self.response_format = response_format

    def message_retrieval(
        self, response: Union[ChatCompletion, Completion]
    ) -> Union[list[str], list[ChatCompletionMessage]]:
        """Retrieve the messages from the response."""
        choices = response.choices

        def format_citations(response):
            if citations := getattr(response, 'citations', []):
                if isinstance(citations, list) and citations:
                    citations_list = '\n'.join(
                        f'[{i+1}] {citation}' for i, citation in enumerate(citations)
                    )
                    return f'\n\nCitations:\n{citations_list}'
            return ''

        citations = format_citations(response)

        if isinstance(response, Completion):
            return [choice.text for choice in choices]

        def _format_content(content: str) -> str:
            return (
                self.response_format.model_validate_json(content).format()
                if isinstance(self.response_format, FormatterProtocol)
                else content
            )

        return [
            (
                choice.message + citations
                if choice.message.function_call is not None
                or choice.message.tool_calls is not None
                else _format_content(choice.message.content) + citations
            )
            for choice in choices
        ]
