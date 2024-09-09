from debtrazor.agents.state import AgentState
from typing import List, Any


class PlannerAgentState(AgentState):
    entry_path: str
    legacy_language: str 
    legacy_framework: str
    new_language: str
    new_framework: str
    legacy_directory_structure: str
    new_directory_structure: str
    dependencies_per_file: dict[str, Any]
    files_to_migrate: List[str]
    unstructured_migration_plan: str