import operator
from typing import Annotated, List
from langchain_core.messages import AnyMessage
from debtrazor.agents.state import AgentState


class DirStructAgentState(AgentState):
    messages: Annotated[list[AnyMessage], operator.add]
    entry_path: str
    legacy_directory_structure: str
    legacy_language: str 
    legacy_framework: str
    new_language: str
    new_framework: str
    files_to_migrate: List[str]