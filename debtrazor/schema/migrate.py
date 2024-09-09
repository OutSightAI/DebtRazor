from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field

class FilesToMigrate(BaseModel): 
    files: List[str] = Field(description="List of relative file paths of the source code files")


class MigrationStep(BaseModel): 
    file_name: str = Field(description="Relative file path of the source code file")
    legacy_context: List[str] = Field(description="List of relative file paths of the source code files that are required to migrate the file")
    new_context: List[str] = Field(description="List of relative file paths of the source code files that are required to migrate the file")
    description: str = Field(description="Description of the file and the context files it requires to migrate the file")

class MigrationPlan(BaseModel): 
    steps: List[MigrationStep] = Field(description="List of migration steps to migrate the source code files")