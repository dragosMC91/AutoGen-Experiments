from pathlib import Path
from sys import argv
import os


def generate_folder_hierarchy(path, indent=0):
    """Generate a text representation of the folder/file hierarchy.

    :param path: The folder path to represent.
    :param indent: The indentation level (used in recursive calls).
    :return: A string representing the folder/file hierarchy.
    """
    hierarchy = ""
    try:
        if os.path.isdir(path):
            # It's a directory, add directory name to the hierarchy
            hierarchy += "    " * indent + os.path.basename(path) + "/\n"
            # Recursively add the contents of the directory to the hierarchy
            with os.scandir(path) as entries:
                for entry in sorted(entries, key=lambda e: e.name):
                    item_path = os.path.join(path, entry.name)
                    hierarchy += generate_folder_hierarchy(item_path, indent + 1)
        else:
            # It's a file, add file name to the hierarchy
            hierarchy += "    " * indent + f"{os.path.basename(path)}\n"
    except OSError as e:
        hierarchy += "    " * indent + f"Error accessing {path}: {e}\n"

    return hierarchy


def generate_sitemap(folder_path, output_file='sitemap.txt'):
    """Generates a sitemap of the specified folder and its subfolders,
    including the contents of all files.

    This function traverses the directory tree starting from `folder_path` and writes a textual sitemap to
    `output_file`. The sitemap includes the path of each file and its contents. If a file cannot be read
    (e.g., due to permissions or it being a binary file), an error message is written to the sitemap.

    Parameters:
    - folder_path (str or pathlib.Path): The path to the folder for which to generate the sitemap.
                                         This can be a string or a pathlib.Path object.
    - output_file (str): The path to the output text file where the sitemap will be written.
                         Defaults to 'sitemap.txt' in the current working directory.
    """

    folder_path = Path(folder_path)
    separator = "======================================="

    if not folder_path.exists():
        print(f"The folder {folder_path} does not exist.")
        return

    with open(output_file, 'w', encoding='utf-8') as sitemap:
        sitemap.write(
            f"Folder structure:\n{separator}\n{generate_folder_hierarchy(folder_path)}\n{separator}\n\n"
        )

        for file_path in sorted(folder_path.glob('**/*')):
            if file_path.is_file():
                sitemap.write(f"File: {file_path}\n")
                try:
                    with open(
                        file_path, 'r', encoding='utf-8', errors='replace'
                    ) as file:
                        sitemap.write(f"Content ({file_path}) START\n{separator}\n")
                        for line in file:
                            sitemap.write(line)
                except Exception as e:
                    sitemap.write(f"Error reading file: {e}\n")

                sitemap.write(f"Content ({file_path}) END\n{separator}\n\n")

    print(f"Sitemap has been generated at {output_file}")


generate_sitemap(argv[1])
