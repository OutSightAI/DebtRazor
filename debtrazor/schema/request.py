from typing import Optional
from pydantic import BaseModel
from debtrazor.schema.model import Model


class AgentParams(BaseModel):
    model: Model
    rerun: Optional[bool]


class AgentRequest(BaseModel):
    document: AgentParams
    planner: AgentParams
    migrate: AgentParams
    entry_path: str
    output_path: str
    legacy_language: str
    legacy_framework: str
    new_language: str
    new_framework: Optional[str]
    langchain_verbose: bool = False
    langchain_tracing: Optional[str] = None

