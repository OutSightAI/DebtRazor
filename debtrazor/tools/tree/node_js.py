import os
import json
import shutil
import subprocess
from langchain_core.tools import tool
from debtrazor.schema.tree import DependencyTree


@tool
def madge(file_path: str) -> DependencyTree:
    """
    Tool for generating internal dependency-tree for Node.js projects.

    Args:
        file_path (str): The path to the Node.js project file for which the dependency tree is to be generated.

    Returns:
        DependencyTree: An object representing the root and dependencies of the project.
        str: An error message if madge is not installed or if an error occurs during execution.
    """
    # Check if madge is installed
    if not shutil.which("madge"):
        return "Madge is not installed. Please install it by running 'npm install -g madge'."

    # Run madge and capture the output
    try:
        result = subprocess.run(
            ["madge", "--json", file_path], capture_output=True, text=True, check=True
        )
        # Parse the JSON output from madge
        full_dependency_tree = json.loads(result.stdout)

        # Create and return a DependencyTree object
        return DependencyTree(
            root=os.path.basename(file_path),
            dependencies=full_dependency_tree[os.path.basename(file_path)],
        )

    except subprocess.CalledProcessError as e:
        # Return an error message if madge execution fails
        return f"An error occurred while running madge: {e.stderr}"
