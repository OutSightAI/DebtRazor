from typing import List, Optional
from pydantic import BaseModel, Field


class DependencyTree(BaseModel):
    """For Outputting Dependency Tree in JSON format"""

    dependencies: Optional[List[str]] = Field(
        description="List of file dependencies in the tree"
    )
    root: str = Field(description="Root of the tree")

    # The 'dependencies' attribute is an optional list of strings that represents
    # the dependencies of the files in the tree.
    # The 'root' attribute is a string that represents the root of the dependency tree.
