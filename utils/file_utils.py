from typing import Optional, Union, List
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import logging
import os
import shutil
import hashlib


def calculate_files_hash(
    input_files: Union[List[str], None] = None, input_dir: Union[str, None] = None
) -> str:
    """Calculate a combined hash of multiple files or all files in a directory.

    Args:
        input_files: List of file paths
        input_dir: Directory path to process recursively

    Returns:
        str: Hexadecimal hash string

    Raises:
        ValueError: If neither input_files nor input_dir is provided
        FileNotFoundError: If any file or directory doesn't exist
    """
    if input_files is None and input_dir is None:
        raise ValueError("Either input_files or input_dir must be provided")

    files_to_process = set()

    # Collect files from input_dir if provided
    if input_dir:
        if not os.path.isdir(input_dir):
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        for root, _, files in os.walk(input_dir):
            for file in files:
                files_to_process.add(os.path.join(root, file))

    # Add individual files if provided
    if input_files:
        for file_path in input_files:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            files_to_process.add(file_path)

    # Calculate combined hash
    hasher = hashlib.sha256()
    buffer_size = 65536  # 64kb chunks

    # Sort files to ensure consistent hash regardless of file order
    for file_path in sorted(files_to_process):
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                hasher.update(data)

    return hasher.hexdigest()


def get_project_root() -> Path:
    return Path(__file__).parent.parent


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
    """Recursively finds specified directories within the start_path.

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
    """Removes specified directories.

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
