import os
from langchain_core.tools import tool
from debtrazor.schema.tree import DependencyTree


@tool
def pydeps(file_path: str) -> DependencyTree:
    """
    Tool for generating internal dependency-tree for python projects.

    Args:
        file_path (str): The path to the Python file for which the dependency tree is to be generated.

    Returns:
        DependencyTree: An object representing the root file and its dependencies.
        If the required package 'import_deps' is not found, a string message is returned instead.
    """
    try:
        from import_deps import __version__, PyModule, ModuleSet
    except ImportError:
        return "Can't find package import_deps. Please run: pip install import_deps"

    # Get the directory of the provided file path
    file_directory = os.path.dirname(file_path)

    # Create a PyModule object for the given file path
    module = PyModule(file_path)

    # Resolve the base path of the module
    base_path = module.pkg_path().resolve()

    # Create a ModuleSet object for all Python files in the base path
    mset = ModuleSet(base_path.glob("**/*.py"))

    # Get the imports for the module, without returning fully qualified names
    imports = mset.get_imports(module, return_fqn=False)

    # Convert the import paths to strings
    imports = [str(path) for path in imports]

    # Get the relative paths of the imports with respect to the file directory
    dependencies = [os.path.relpath(path, file_directory) for path in imports]

    # Return a DependencyTree object with the root file and its dependencies
    return DependencyTree(root=os.path.basename(file_path), dependencies=dependencies)
