from typing import Optional
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import logging
import os
import shutil

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

def find_junk_dirs(start_path, junk_dirs):
    """
    Recursively finds specified directories within the start_path.

    :param start_path: The directory path to start searching from.
    :param junk_dirs: A list of directory names to find.
    :return: A list of directories to be removed.
    """
    dirs_to_remove = []
    for root, dirs, _ in os.walk(start_path, topdown=False):
        for name in dirs:
            if name in junk_dirs:
                full_path = os.path.join(root, name)
                dirs_to_remove.append(full_path)
    return dirs_to_remove

def remove_junk_dirs(dirs_to_remove):
    """
    Removes specified directories.

    :param dirs_to_remove: A list of directories to remove.
    """
    print("The following directories will be deleted:")
    for dir_path in dirs_to_remove:
        print(dir_path)
    confirmation = input("Do you want to proceed? (yes/no): ")

    if confirmation.lower() == 'yes':
        for dir_path in dirs_to_remove:
            try:
                shutil.rmtree(dir_path)
                print(f"Removed: {dir_path}")
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")
    else:
        print("Operation cancelled.")
