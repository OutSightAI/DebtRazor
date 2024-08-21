# migrate_utils

Welcome to the `migrate_utils` module! This directory contains various scripts and utilities designed to facilitate the migration and documentation processes within the `debtrazor` package. Below is a brief overview of each file/module in this directory to help you get started quickly.

## File/Module Summaries

### run_doc_agent.py
This script defines an asynchronous function `run_documentation_agent` that processes documentation for a repository using the `DocAgent` class. The function:
- Initializes the `DocAgent` with a language model and tools.
- Checks the current state of the documentation process.
- Decides whether to continue or finalize the documentation.
- Logs relevant information and updates the state accordingly.

**Internal Dependencies:**
- `../tools/tree/python.py`
- `../agents/doc_agent/agent.py`
- `llm.py`
- `../utils/logging.py`
- `../tools/tree/node_js.py`

### utils.py
This file is currently empty. Please provide content for a proper summary.

**Internal Dependencies:**
- None

### llm.py
This script defines a function `get_llm` that retrieves a language model (LLM) based on specified model parameters. The function:
- Reads configuration details from a `llm.yaml` file located in a predefined configuration directory.
- Supports only OpenAI's completion models.
- Raises appropriate errors if the model name, type, or API is not recognized.

**Internal Dependencies:**
- None

### __init__.py
This file is part of the `debtrazor` package and is responsible for setting up the environment and running various agents related to migration and documentation. It imports specific setup functions and a documentation agent runner. The `__all__` list defines the public interface of the module.

**Internal Dependencies:**
- `run_doc_agent.py`
- `setup.py`

### setup.py
This script is designed to set up and manage the environment for a project using the `debtrazor` and `langchain` libraries. It includes functions for:
- Configuring langchain tracing.
- Setting up the environment and logging.
- Initializing memory with a SQLite database.
- Creating the initial state for a `DocAgent`.

The code ensures proper directory permissions, sets verbosity levels, and reads `.gitignore` files to manage ignored paths.

**Internal Dependencies:**
- `../utils/cfg.py`
- `../utils/logging.py`
- `../utils/util.py`

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd migrate_utils
   ```

2. **Install Dependencies:**
   Ensure you have all the necessary dependencies installed. You can use `pip` to install them:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Documentation Agent:**
   You can start the documentation process by running the `run_doc_agent.py` script:
   ```bash
   python run_doc_agent.py
   ```

4. **Explore Other Utilities:**
   Check out the other scripts and modules to understand their functionalities and how they can assist in your migration and documentation tasks.

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Feel free to reach out if you have any questions or need further assistance. Happy coding!