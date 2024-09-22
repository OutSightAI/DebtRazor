import os
import fnmatch
import re
from debtrazor.utils.logging import logging


def read_gitignore(path):
    """
    Reads the .gptignore file from the given path and extracts the patterns to ignore.

    Args:
        path (str): The directory path where the .gptignore file is located.

    Returns:
        list: A list of patterns to ignore as specified in the .gptignore file.
    """
    logging.info("Reading .gptignore")
    gitignore_path = os.path.join(path, ".gptignore")
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as file:
            for line in file:
                line = line.strip()  # Remove leading and trailing whitespace
                if line and not line.startswith("#"):  # Ignore empty lines and comments
                    patterns.append(line)
    logging.info("Ignoring the following files: %s", patterns)
    return patterns


def is_ignored(entry_path, gitignore_patterns):
    """
    Checks if a given file path matches any of the ignore patterns.

    Args:
        entry_path (str): The file path to check.
        gitignore_patterns (list): A list of patterns to ignore.

    Returns:
        bool: True if the file path matches any ignore pattern, False otherwise.
    """
    for pattern in gitignore_patterns:
        if fnmatch.fnmatch(
            entry_path, pattern
        ):  # Check if the file path matches the pattern
            return True
    return False


def parse_code_string(code_string):
    """
    Extracts the code block from a given string formatted with triple backticks.

    Args:
        code_string (str): The string containing the code block.

    Returns:
        str: The extracted code block if found, otherwise the original string.
    """
    pattern = re.compile(
        r"```(.+?)\n(.*?)\n```", re.DOTALL
    )  # Regex to match code block
    match = pattern.match(code_string)
    if match:
        _, code = match.groups()  # Extract the code block
        return code
    return code_string


def get_relative_path(path, entry_path):
    """
    Computes the relative path from the entry path to the given path.

    Args:
        path (str): The full path.
        entry_path (str): The entry path to compute the relative path from.

    Returns:
        str: The relative path from the entry path to the given path.
    """
    start_pos = path.find(
        entry_path
    )  # Find the start position of the entry path in the full path
    relative_path = path[start_pos + len(entry_path):]  # Compute the relative path
    if relative_path is not None and len(relative_path) > 0:
        if relative_path[0] == "/":  # Remove leading slash if present
            relative_path = relative_path[1:]
    return relative_path

def filter_dict_by_keys(input_dict:dict, allowed_keys: list):
    """
    Filter a dictionary by a list of keys.

    Args:
        input_dict (dict): The input dictionary to filter.
        keys (list): A list of keys to keep in the dictionary.

    Returns:
        dict: The filtered dictionary.
    """
    return dict(filter(lambda item: item[0] in allowed_keys, input_dict.items()))