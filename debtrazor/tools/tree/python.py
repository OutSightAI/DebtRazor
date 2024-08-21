import os
from langchain_core.tools import tool
from debtrazor.schema.tree import DependencyTree


@tool
def pydeps(file_path: str) -> DependencyTree:
    """Tool for generating internal dependency-tree for python projects."""
    try:
        from import_deps import __version__, PyModule, ModuleSet
    except ImportError:
        return f"Can't find package import_deps. Please run: pip install import_deps"

    file_directory = os.path.dirname(file_path)
    module = PyModule(file_path)
    base_path = module.pkg_path().resolve()
    mset = ModuleSet(base_path.glob("**/*.py"))

    imports = mset.get_imports(module, return_fqn=False)
    imports = [str(path) for path in imports]

    dependencies = [os.path.relpath(path, file_directory) for path in imports]

    return DependencyTree(root=os.path.basename(file_path), dependencies=dependencies)
