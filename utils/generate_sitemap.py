from pathlib import Path
import os
import sys
import chardet


def generate_folder_hierarchy(path, indent=0, ignore_items=None):
    """Generate a text representation of the folder/file hierarchy.

    :param path: The folder path to represent.
    :param indent: The indentation level (used in recursive calls).
    :param ignore_items: List of folder names to ignore.
    :return: A string representing the folder/file hierarchy.
    """
    hierarchy = ""
    try:
        if os.path.isdir(path):
            folder_name = os.path.basename(path)
            if ignore_items and folder_name in ignore_items:
                return ""
            # It's a directory, add directory name to the hierarchy
            hierarchy += "    " * indent + folder_name + "/\n"
            # Recursively add the contents of the directory to the hierarchy
            with os.scandir(path) as entries:
                for entry in sorted(entries, key=lambda e: e.name):
                    item_path = os.path.join(path, entry.name)
                    hierarchy += generate_folder_hierarchy(
                        item_path, indent + 1, ignore_items
                    )
        else:
            # It's a file, add file name to the hierarchy
            hierarchy += "    " * indent + f"{os.path.basename(path)}\n"
    except OSError as e:
        hierarchy += "    " * indent + f"Error accessing {path}: {e}\n"

    return hierarchy


def generate_sitemap(
    folder_path, ignore_items=['.git', 'node_modules', '.DS_Store', '.vscode']
):
    """Generates a sitemap of the specified folder and its subfolders,
    including the contents of all files.

    This function traverses the directory tree starting from `folder_path` and creates a textual sitemap
    The sitemap includes the path of each file and its contents. If a file cannot be read
    (e.g., due to permissions or it being a binary file), an error message is written to the sitemap.

    Parameters:
    - folder_path (str or pathlib.Path): The path to the folder for which to generate the sitemap.
                                         This can be a string or a pathlib.Path object.
    - ignore_items (list): List of folder names to ignore (e.g., ['.git', 'node_modules']).
    """

    folder_path = Path(folder_path)
    separator = "======================================="

    if not folder_path.exists():
        print(f"The folder {folder_path} does not exist.")
        return

    sitemap = ''
    sitemap += f"Folder structure:\n{separator}\n{generate_folder_hierarchy(folder_path,ignore_items=ignore_items)}\n{separator}\n\n"
    for file_path in sorted(folder_path.glob('**/*')):
        if any(ignored in file_path.parts for ignored in (ignore_items or [])):
            continue
        if file_path.is_file():
            sitemap += f"File: {file_path}\n"
            try:
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                    text = raw_data.decode(encoding)
                    sitemap += f"Content ({file_path}) START\n{separator}\n"
                    sitemap += text
            except Exception as e:
                sitemap += f"Error reading file: {e}\n"

            sitemap += f"Content ({file_path}) END\n{separator}\n\n"
    return sitemap


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <folder_path> ignore_item1, ignore_item2 ...")
        sys.exit(1)

    folder_path = sys.argv[1]
    default_ignore_items = ['.git', 'node_modules', '.DS_Store']
    ignore_items = (
        sys.argv[2:] + default_ignore_items
        if len(sys.argv) > 2
        else default_ignore_items
    )

    sitemap_text = generate_sitemap(folder_path, ignore_items=ignore_items)
    with open('sitemap.txt', 'w', encoding='utf-8') as sitemap:
        sitemap.write(sitemap_text)
