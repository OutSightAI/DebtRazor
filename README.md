# Debtrazor

## Demo (click image to watch)
[![Demo](./debtrazor/assets/debtrazor.webp)](https://www.youtube.com/watch?v=miZnZOtuTvk "Demo") 

Lets cleanse the world of tech debt, one repo at a time.


## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/OutSightAI/DebtRazor
   cd debtrazor
   ```

2. **Install Dependencies:**
   Ensure you have all the necessary dependencies installed. You can use `pip` to install them:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Main Script:**
   - Create a virtual environment and activate it: (optional)
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   - Export the PYTHONPATH environment variable to include the project directory:
   ```bash
   export PYTHONPATH=$(pwd)
   ```

   - Modify the `configs/config.yaml` file 
   ```yaml
   entry_path: "/path/to/project"
   output_path: "./path/to/output"
   ```

   - You can now start the migration process by running the `main.py` script:
   ```bash
   python main.py
   ```

(Note: All of this project was documented by DebtRazor itself, with minimal human edits.)

## Overview
This repository contains various modules and utilities designed to facilitate code migration, documentation generation, and dependency management. Below is an overview of the key directories and files within this project to help you get started quickly.

## Directory Structure

- `main.py`
- `agents/`
- `schema/`
- `tools/`
- `migrate_utils/`
- `utils/`

## File/Module Summaries

### `main.py`
The `main.py` file is an asynchronous Python script designed to orchestrate a code migration process. It performs the following key steps:
1. Loads and validates the configuration.
2. Sets up the environment based on the configuration.
3. Sets up long-term memory for the agents.
4. Creates the initial state for the migration.
5. Runs the documentation agent.

**Internal Dependencies:** 
- `utils/__init__.py`
- `migrate_utils/setup.py`
- `migrate_utils/__init__.py`

### `agents/`
The `agents` module facilitates the creation and management of agents for various tasks, including documentation generation and code processing.

#### Key Files and Submodules:
- `agent.py`: Defines an abstract base class `Agent`.
- `__init__.py`: Empty initializer for the module.
- `doc_agent/`: Submodule for documentation agents.
  - `prompts.py`: Defines templates and prompt configurations.
  - `agent.py`: Defines the `DocAgent` class.
  - `__init__.py`: Empty initializer for the submodule.
  - `state.py`: Manages the state of a documentation agent.
- `state.py`: Defines the `AgentState` class.

### `schema/`
The `schema` directory contains various Pydantic models and classes for data validation, settings management, and representing different entities and requests within the system.

#### Key Files:
- `model.py`: Defines a Pydantic model named `Model`.
- `request.py`: Defines `AgentParams` and `AgentRequest` classes.
- `__init__.py`: Empty initializer for the module.
- `tree.py`: Defines a `DependencyTree` class.

### `tools/`
The `tools` module contains various utilities and tools designed to assist in the development and maintenance of your projects.

#### Key Files and Submodules:
- `__init__.py`: Empty initializer for the module.
- `utils.py`: Defines a function `execute_tool`.
- `tree/`: Submodule for generating internal dependency trees.
  - `__init__.py`: Empty initializer for the submodule.
  - `python.py`: Defines a tool named `pydeps`.
  - `node_js.py`: Defines a tool named `madge`.
- `dependency_tree/`: Submodule for managing and visualizing dependencies.
  - `parser.py`, `visualizer.py`, `analyzer.py`, `config.py`, `utils.py`, `README.md`

### `migrate_utils/`
The `migrate_utils` module contains various scripts and utilities designed to facilitate the migration and documentation processes.

#### Key Files:
- `run_doc_agent.py`: Defines an asynchronous function `run_documentation_agent`.
- `utils.py`: Currently empty.
- `llm.py`: Defines a function `get_llm`.
- `__init__.py`: Sets up the environment and runs various agents.
- `setup.py`: Manages the environment for a project using the `debtrazor` and `langchain` libraries.

### `utils/`
The `utils` directory contains various utility modules that provide essential functionalities for handling configuration files, logging, directory structures, and more.

#### Key Files:
- `util.py`: Contains utility functions for handling `.gptignore` files, checking file paths, extracting code blocks, and computing relative paths.
- `logging.py`: Provides a global logging setup for the application.
- `__init__.py`: Imports the `load_and_validate_config` function.
- `generate_readme.py`: Generates a comprehensive README file for a project directory.
- `tree.py`: Generates a visual tree structure of a directory.
- `load.py`: Handles the loading, parsing, and validation of configuration data from a YAML file.
- `cfg.py`: Defines a `Config` class for configuration management.

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Feel free to reach out if you have any questions or need further assistance. Happy coding!