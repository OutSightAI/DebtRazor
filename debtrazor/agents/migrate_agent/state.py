import operator
from typing import Any, List, Annotated
from langchain_core.messages import AnyMessage
from debtrazor.agents.state import AgentState
from debtrazor.schema.migrate import MigrationStep

class MigrateAgentState(AgentState):
    messages: Annotated[list[AnyMessage], operator.add]
    entry_path: str
    output_path: str
    legacy_language: str
    new_language: str
    new_directory_structure: str
    current_plan: str
    file_to_migrate: MigrationStep
    