from pathlib import Path
from typing import List, Tuple, Optional
import os
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


def read_file_content(file_path: Path) -> str:
    """Read file content with basic error handling and size limit."""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > 100_000:  # 100 KB limit
            return f"[File content not shown. Size: {file_size} bytes]"

        with file_path.open("r", encoding="utf-8", errors="replace") as f:
            return f.read(1000)  # Read only the first 1000 characters
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def generate_comprehensive_readme(
    root_path: str | Path, ignore_patterns: Optional[List[str]] = None
) -> str:
    root_path = Path(root_path).resolve()
    ignore_patterns = ignore_patterns or []

    def traverse(path: Path, depth: int = 0) -> List[Tuple[int, str, str]]:
        result = []
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items:
            if should_ignore(item, root_path, ignore_patterns):
                continue

            relative_path = item.relative_to(root_path)
            indent = "  " * depth

            if item.is_dir():
                result.append((depth, f"{indent}📁 {item.name}/", ""))
                result.extend(traverse(item, depth + 1))
            elif item.name.lower() == "readme.md":
                content = read_file_content(item)
                result.append((depth, f"{indent}📄 {item.name}", content))
            else:
                result.append((depth, f"{indent}📄 {item.name}", ""))

        return result

    structure = traverse(root_path)

    output = [f"# {root_path.name} Project Overview\n"]
    output.append("## Directory Structure and Documentation\n")

    for depth, item, content in structure:
        output.append(item)
        if content:
            output.append("\n```markdown")
            output.append(content)
            output.append("```\n")

    return "\n".join(output)
