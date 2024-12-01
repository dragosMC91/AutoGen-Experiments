from typing import Optional
from pathlib import Path
import os
from dataclasses import dataclass
from utils import file_utils

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


@dataclass
class QueryEngineConfig:
    """Configuration for the QueryEngine."""

    # input_files takes precedence over input_dir and is recommended
    input_files: list[str]
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    persist_dir: str = None
    input_dir: str = None
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-2024-11-20"
    temperature: float = 0.0


# query engine can be tweaked and enhanced: https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/usage_pattern/#query-engine-tools
class DocumentQueryEngine:
    """A class to manage document querying using LlamaIndex."""

    _instance = None

    def __init__(self, config: QueryEngineConfig):
        """Initialize the query engine with the given configuration."""
        self.config = config
        self._query_engine = None
        self._setup_models()

    @classmethod
    def get_instance(
        cls, config: Optional[QueryEngineConfig] = None
    ) -> 'DocumentQueryEngine':
        """Get or create a singleton instance of DocumentQueryEngine."""
        if cls._instance is None:
            if config is None:
                raise ValueError("Configuration required for first initialization")
            cls._instance = cls(config)
        return cls._instance

    def _setup_models(self) -> None:
        """Setup the embedding and language models."""
        embed_model = OpenAIEmbedding(
            model=self.config.embedding_model,
            temperature=self.config.temperature,
            api_key=self.config.openai_api_key,
        )
        llm = OpenAI(
            model=self.config.llm_model,
            temperature=self.config.temperature,
            api_key=self.config.openai_api_key,
        )
        Settings.embed_model = embed_model
        Settings.llm = llm

    # https://docs.llamaindex.ai/en/stable/getting_started/starter_example/
    def _initialize_query_engine(self) -> None:
        """Initialize the query engine, either from persistence or from
        documents."""
        if self.config.persist_dir:
            persist_path = Path(self.config.persist_dir)
        else:
            # if any files are changed, a new storage is created and cached
            input_content_hash = file_utils.calculate_files_hash(
                input_dir=self.config.input_dir, input_files=self.config.input_files
            )
            persist_path = Path(
                f"{file_utils.get_project_root()}/generated_content/embeddings/${input_content_hash}"
            )

        if persist_path.exists():
            storage_context = StorageContext.from_defaults(
                persist_dir=str(persist_path)
            )
            index = load_index_from_storage(storage_context)
        else:
            documents = SimpleDirectoryReader(
                input_files=self.config.input_files, input_dir=self.config.input_dir
            ).load_data(show_progress=True)
            index = VectorStoreIndex.from_documents(
                documents=documents, show_progress=True
            )
            persist_path.parent.mkdir(parents=True, exist_ok=True)
            index.storage_context.persist(persist_dir=str(persist_path))

        self._query_engine = index.as_query_engine()

    @property
    def query_engine(self) -> BaseQueryEngine:
        """Get the query engine, initializing it if necessary."""
        if self._query_engine is None:
            self._initialize_query_engine()
        return self._query_engine

    def query(self, question: str) -> str:
        """Query the document index with a question.

        Args:
            question (str): The question to ask

        Returns:
            str: The response from the query engine
        """
        try:
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            raise Exception(f"Error querying the engine: {str(e)}")
