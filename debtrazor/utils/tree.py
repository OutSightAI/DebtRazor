from pathlib import Path
from typing import Optional, List
import fnmatch


def should_ignore(path: Path, base_path: Path, ignore_patterns: List[str]) -> bool:
    """Check if a path should be ignored based on the ignore patterns"""
    rel_path = path.relative_to(base_path)
    str_path = str(rel_path)
    return any(
        fnmatch.fnmatch(str_path, pattern)
        or fnmatch.fnmatch(str_path + "/", pattern)
        or any(fnmatch.fnmatch(part, pattern) for part in rel_path.parts)
        for pattern in ignore_patterns
    )


def tree(
    dir_path: str | Path,
    level: int = -1,
    limit_to_directories: bool = False,
    length_limit: int = 1000,
    ignore_patterns: Optional[List[str]] = None,
) -> str:
    """
    Given a directory path, print a visual tree structure

    Args:
    - dir_path: Path of the directory to visualize
    - level: Maximum depth of the tree (-1 for unlimited)
    - limit_to_directories: If True, only show directories
    - length_limit: Maximum number of lines to print
    - ignore_patterns: List of patterns to ignore

    Returns:
    - String representation of the directory tree
    """
    dir_path = Path(dir_path).resolve()
    ignore_patterns = ignore_patterns or []
    files = 0
    directories = 0
    output = [dir_path.name]

    def inner(dir_path: Path, prefix: str = "", level: int = -1) -> List[str]:
        nonlocal files, directories
        if level == 0:
            return []

        contents = [
            d
            for d in dir_path.iterdir()
            if not should_ignore(d, dir_path, ignore_patterns)
        ]
        if limit_to_directories:
            contents = [d for d in contents if d.is_dir()]

        pointers = ["├── "] * (len(contents) - 1) + ["└── "]
        result = []
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                result.append(f"{prefix}{pointer}{path.name}")
                directories += 1
                extension = "│   " if pointer == "├── " else "    "
                result.extend(inner(path, prefix=prefix + extension, level=level - 1))
            elif not limit_to_directories:
                result.append(f"{prefix}{pointer}{path.name}")
                files += 1
        return result

    output.extend(inner(dir_path, level=level))

    if len(output) > length_limit:
        output = output[:length_limit]
        output.append(f"... length_limit, {length_limit}, reached, counted:")

    output.append(
        f"\n{directories} directories" + (f", {files} files" if files else "")
    )

    return "\n".join(output)
