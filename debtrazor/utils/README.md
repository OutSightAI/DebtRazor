# utils Directory

Welcome to the `utils` directory! This directory contains various utility modules that provide essential functionalities for handling configuration files, logging, directory structures, and more. Below is a brief overview of each file/module within this directory:

## File/Module Summaries

### 1. `util.py`
This module contains utility functions for handling `.gptignore` files, checking file paths against ignore patterns, extracting code blocks from strings, and computing relative paths. Key functions include:
- **`read_gitignore(path)`**: Reads a `.gptignore` file from the specified directory and returns a list of patterns to ignore.
- **`is_ignored(entry_path, gitignore_patterns)`**: Checks if a given file path matches any of the ignore patterns.
- **`parse_code_string(code_string)`**: Extracts a code block from a string formatted with triple backticks.
- **`get_relative_path(path, entry_path)`**: Computes the relative path from an entry path to a given path.

**Internal Dependencies**: `logging.py`

### 2. `logging.py`
This module provides a global logging setup for the application. It includes:
- **`add_to_log_queue`**: An asynchronous function to add log messages to an asyncio queue with a simulated delay.
- **`setup_logger`**: Configures a logger with a specified name and logging level, setting up a console handler with a specific log message format.

A default logger named "gpt_migrate" is created for the entire application.

**Internal Dependencies**: None

### 3. `__init__.py`
This module imports the `load_and_validate_config` function from the `debtrazor.utils.load` module, which is used for loading and validating configuration files. The `__all__` list is defined to specify that `load_and_validate_config` is the only attribute accessible when the module is imported using `from module import *`.

**Internal Dependencies**: `load.py`

### 4. `generate_readme.py`
This module provides functionality to generate a comprehensive README file for a project directory. Key functions include:
- **`should_ignore`**: Determines if a given path should be ignored based on specified ignore patterns.
- **`read_file_content`**: Reads the content of a file with basic error handling and a size limit.
- **`generate_comprehensive_readme`**: Generates a README file that outlines the directory structure and includes the content of README.md files found within the directory.

**Internal Dependencies**: None

### 5. `tree.py`
This module provides functionality to generate a visual tree structure of a directory. Key functions include:
- **`should_ignore`**: Determines if a given path should be ignored based on specified ignore patterns.
- **`tree`**: Generates a string representation of the directory tree, with options to limit the depth, include only directories, and apply ignore patterns.

**Internal Dependencies**: None

### 6. `load.py`
This module handles the loading, parsing, and validation of configuration data from a YAML file. Key functions include:
- **`load_config(config_path: str) -> dict[str, Any]`**: Loads and returns configuration data from a specified YAML file.
- **`parse_arguments() -> argparse.Namespace`**: Parses command line arguments to obtain the path to the configuration file.
- **`load_and_validate_config(config_data: AgentRequest | None = None, log_queue: asyncio.Queue | None = None) -> Config`**: Asynchronously loads and validates the configuration data.

**Internal Dependencies**: `logging.py`, `cfg.py`, `../schema/request.py`

### 7. `cfg.py`
This module defines a `Config` class that converts a configuration dictionary into an object with attributes accessible via dot notation. The class includes methods to:
- Recursively wrap dictionary values into `Config` objects.
- Handle collections by wrapping their elements.
- Convert relative paths to absolute paths for specified keys.
- Provide a string representation method to recursively convert the `Config` object into a readable string format.

**Internal Dependencies**: None

## Getting Started

To get started with the `utils` directory, you can explore the individual modules and their functionalities as described above. Each module is well-documented and designed to be easy to understand and extend. If you have any questions or need further assistance, please refer to the documentation within each module or reach out to the maintainers.

Happy coding!