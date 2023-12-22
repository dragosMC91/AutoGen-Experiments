from typing import Optional
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import logging


def load_env(dotenv_file_path: Optional[str] = None):
    """Load configurations from a specified .env file.

    Args:
        dotenv_file_path (str, optional): The path to the .env file. Defaults to None.
    """

    if dotenv_file_path:
        dotenv_path = Path(dotenv_file_path)
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
        else:
            logging.warning(f"The specified .env file {dotenv_path} does not exist.")
    else:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            logging.warning(
                "No .env file found. Loading configurations from environment variables."
            )
        load_dotenv(dotenv_path)
