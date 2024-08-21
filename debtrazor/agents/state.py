import operator
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage


class AgentState(TypedDict):
    """
    A TypedDict class representing the state of an agent.

    Attributes:
    -----------
    messages : Annotated[list[AnyMessage], operator.add]
        A list of messages of type AnyMessage. The Annotated type is used here
        with operator.add, which might be used for some specific type checking
        or validation purposes.
    """

    messages: Annotated[list[AnyMessage], operator.add]
