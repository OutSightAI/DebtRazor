import os
import json
import shutil
import subprocess
from langchain_core.tools import tool
from debtrazor.schema.tree import DependencyTree


@tool
def madge(file_path: str) -> DependencyTree:
    """Tool for generating internal dependency-tree for nodejs projects."""
    # Check if madge is installed

    if not shutil.which("madge"):
        return "Madge is not installed. Please install it by running 'npm \
            install -g madge'."

    # Run madge and capture the output
    try:
        result = subprocess.run(
            ["madge", "--json", file_path], capture_output=True, text=True, check=True
        )
        full_dependency_tree = json.loads(result.stdout)

        return DependencyTree(
            root=os.path.basename(file_path),
            dependencies=full_dependency_tree[os.path.basename(file_path)],
        )

    except subprocess.CalledProcessError as e:
        return f"An error occurred while running madge: {e.stderr}"
