from debtrazor.agents.state import AgentState
from typing import Any


class DocAgentState(AgentState):
    """
    DocAgentState is a class that extends AgentState to manage the state of a documentation agent.

    Attributes:
        entry_path (str): The initial path where the documentation process starts.
        output_path (str): The path where the output documentation will be saved.
        current_path (str): The current path being processed.
        current_file (str): The current file being processed.
        ignore_list (list[str]): A list of file or directory names to be ignored during processing.
        items_to_process (list[str]): A list of items (files/directories) that need to be processed.
        directory_structure (str): The structure of the directory being processed.
        directory_stack (list[dict[str, Any]]): A stack to keep track of directory states.
        dependencies_per_file (dict[str, Any]): A dictionary to track dependencies for each file.
        legacy_language (str): The legacy programming language being documented.
        legacy_framework (str): The legacy framework being documented.
        indent (str): The indentation style used in the documentation.
    """

    entry_path: str
    output_path: str
    current_path: str
    current_file: str
    ignore_list: list[str]
    items_to_process: list[str] = []
    directory_structure: str
    directory_stack: list[dict[str, Any]]
    dependencies_per_file: dict[str, Any]
    legacy_language: str
    legacy_framework: str
    indent: str
