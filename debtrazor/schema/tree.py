from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel, Field


class DependencyTree(BaseModel):
    """For Outputting Dependency Tree in JSON format"""

    dependencies: Optional[List[str]] = Field(
        description="List of file dependencies in the tree"
    )
    root: str = Field(description="Root of the tree")


