import os
import re

def extract_use_statements(file_path):
    """
    Extracts 'use' statements from a Rust file.
    
    Args:
        file_path (str): The path to the Rust file.
    
    Returns:
        list: A list of 'use' statements from the Rust file.
    """
    # Regex pattern to match Rust 'use' statements
    use_pattern = re.compile(r'^\s*use\s+[\w:]+[;,]?.*$')
    
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            use_statements = [line.strip() for line in lines if use_pattern.match(line)]
            return use_statements
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return []

def extract_all_dependencies(directory_path: str) -> dict[str, list[str]]:
    """Recursively extract `use` statements from all Rust files in the directory."""
    result = {}

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".rs"):
                # Get the relative file path
                relative_file_path = os.path.relpath(os.path.join(root, file), directory_path)
                
                # Extract `use` statements from this file
                use_statements = extract_use_statements(os.path.join(root, file))
                
                if use_statements:
                    result[relative_file_path] = use_statements
    
    return result

