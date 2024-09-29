import os
import re
import aiofiles
from typing import List
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from debtrazor.utils.util import filter_dict_by_keys, parse_code_string

from langchain_core.language_models import BaseChatModel




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

async def generate_cargo_toml(
    directory_path: str, 
    migrated_files: List[str], 
    output_path: str, 
    llm: BaseChatModel,
) -> str: 
    
    use_statements = extract_all_dependencies(directory_path)
    use_statements = filter_dict_by_keys(use_statements, migrated_files)

    # Generate the Cargo.toml file
    system_prompt = """You are a helpful assistant that generates Cargo.toml files for Rust projects. 
                        Keep your answer restricted to the cargo.toml file and no extra comments or 
                        additional verbosity."""    
    human_prompt = """Given the following use statements from Rust files:\n\n{use_statements}
                        \n\nGenerate a Cargo.toml file that includes the necessary dependencies."""
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt)
        ]
    )

    chain = prompt | llm
    cargo_toml_content = await chain.ainvoke({"use_statements": use_statements})
 
    async with aiofiles.open(os.path.join(output_path, "Cargo.toml"), 'w') as f:
        await f.write(parse_code_string(cargo_toml_content.content))

    return os.path.join(output_path, "Cargo.toml")