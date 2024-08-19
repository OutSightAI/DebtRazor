from gpt_migrate.agents.state import AgentState
from typing import Any


class DocAgentState(AgentState):
    entry_path: str
    output_path: str
    current_path: str
    current_file: str
    ignore_list: list[str]
    items_to_process: list[str]
    directory_structure: str
    directory_stack: list[dict[str, Any]]
    dependencies_per_file: dict[str, Any]
    legacy_language: str
    legacy_framework: str
    indent: str
