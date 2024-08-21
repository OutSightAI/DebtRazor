from typing import Optional
from pydantic import BaseModel
from debtrazor.schema.model import Model


class AgentParams(BaseModel):
    """
    A class to represent the parameters for an agent.

    Attributes:
    ----------
    model : Model
        The model to be used by the agent.
    rerun : Optional[bool]
        A flag indicating whether to rerun the agent. Default is None.
    """

    model: Model
    rerun: Optional[bool]


class AgentRequest(BaseModel):
    """
    A class to represent a request to an agent.

    Attributes:
    ----------
    document : AgentParams
        Parameters for the document agent.
    planner : AgentParams
        Parameters for the planner agent.
    migrate : AgentParams
        Parameters for the migrate agent.
    entry_path : str
        The entry path for the agent to process.
    output_path : str
        The output path where the agent will store results.
    legacy_language : str
        The legacy programming language being used.
    legacy_framework : str
        The legacy framework being used.
    new_language : str
        The new programming language to migrate to.
    new_framework : Optional[str]
        The new framework to migrate to. Default is None.
    langchain_verbose : bool
        A flag indicating whether to enable verbose logging for langchain. Default is False.
    langchain_tracing : Optional[str]
        A string for langchain tracing configuration. Default is None.
    """

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
