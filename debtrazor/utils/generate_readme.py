from pathlib import Path
from typing import List, Tuple, Optional
import os
import fnmatch


def should_ignore(path: Path, base_path: Path, ignore_patterns: List[str]) -> bool:
    """
    Check if a path should be ignored based on the ignore patterns.

    Args:
        path (Path): The path to check.
        base_path (Path): The base path to which the relative path is calculated.
        ignore_patterns (List[str]): A list of patterns to ignore.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    rel_path = path.relative_to(base_path)  # Get the relative path
    str_path = str(rel_path)  # Convert the relative path to string
    return any(
        fnmatch.fnmatch(str_path, pattern)  # Check if the path matches the pattern
        or fnmatch.fnmatch(
            str_path + "/", pattern
        )  # Check if the path with trailing slash matches the pattern
        or any(
            fnmatch.fnmatch(part, pattern) for part in rel_path.parts
        )  # Check if any part of the path matches the pattern
        for pattern in ignore_patterns
    )


def read_file_content(file_path: Path) -> str:
    """
    Read file content with basic error handling and size limit.

    Args:
        file_path (Path): The path of the file to read.

    Returns:
        str: The content of the file or an error message if the file cannot be read.
    """
    try:
        file_size = os.path.getsize(file_path)  # Get the size of the file
        if file_size > 100_000:  # 100 KB limit
            return f"[File content not shown. Size: {file_size} bytes]"

        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            return f.read(1000)  # Read only the first 1000 characters
    except Exception as e:
        return f"[Error reading file: {str(e)}]"  # Return error message if file cannot be read


def generate_comprehensive_readme(
    root_path: str | Path, ignore_patterns: Optional[List[str]] = None
) -> str:
    """
    Generate a comprehensive README file for a project directory.

    Args:
        root_path (str | Path): The root path of the project directory.
        ignore_patterns (Optional[List[str]]): A list of patterns to ignore.

    Returns:
        str: The content of the generated README file.
    """
    root_path = Path(root_path).resolve()  # Resolve the root path
    ignore_patterns = ignore_patterns or []  # Use empty list if ignore_patterns is None

    def traverse(path: Path, depth: int = 0) -> List[Tuple[int, str, str]]:
        """
        Traverse the directory structure recursively.

        Args:
            path (Path): The current path to traverse.
            depth (int): The current depth in the directory structure.

        Returns:
            List[Tuple[int, str, str]]: A list of tuples containing depth, item description, and content.
        """
        result = []
        items = sorted(
            path.iterdir(), key=lambda x: (not x.is_dir(), x.name)
        )  # Sort items, directories first

        for item in items:
            if should_ignore(
                item, root_path, ignore_patterns
            ):  # Check if the item should be ignored
                continue

            indent = "  " * depth  # Create indentation based on depth

            if item.is_dir():
                result.append(
                    (depth, f"{indent}📁 {item.name}/", "")
                )  # Append directory to result
                result.extend(
                    traverse(item, depth + 1)
                )  # Recursively traverse the directory
            elif item.name.lower() == "readme.md":
                content = read_file_content(item)  # Read the content of README.md
                result.append(
                    (depth, f"{indent}📄 {item.name}", content)
                )  # Append README.md to result with content
            else:
                result.append(
                    (depth, f"{indent}📄 {item.name}", "")
                )  # Append file to result without content

        return result

    structure = traverse(root_path)  # Get the directory structure

    output = [f"# {root_path.name} Project Overview\n"]
    output.append("## Directory Structure and Documentation\n")

    for depth, item, content in structure:
        output.append(item)
        if content:
            output.append("\n```markdown")
            output.append(content)
            output.append("```\n")

    return "\n".join(output)
