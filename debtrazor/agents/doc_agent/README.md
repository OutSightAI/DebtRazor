# doc_agent

Welcome to the `doc_agent` module! This module is designed to facilitate the documentation of code directories and files. It includes various tools and classes to generate detailed documentation, summaries, README.md files, and dependency trees. Below is an overview of the files and their functionalities within this module:

## Files and Modules

### prompts.py
This file defines a set of templates and prompt configurations for generating detailed documentation, summaries, README.md files, and dependency trees for code files. It uses the `ChatPromptTemplate` class from the `langchain_core.prompts.chat` module to create instances of these templates. Each template includes a system prompt and a human prompt, guiding the user on how to provide the necessary input and what the expected output should be. The templates are designed to ensure that the codebase is well-documented, easy to understand, and maintainable.

**Internal Dependencies:** None

### agent.py
This file defines the `DocAgent` class, a specialized agent for processing and documenting code directories and files. The `DocAgent` class extends from a base `Agent` class and utilizes various tools and models to generate documentation, summaries, and dependency trees for code files. The agent operates through a state graph (`StateGraph`) with nodes and conditional edges to manage the flow of processing directories and files.

Key functionalities include:
1. **Initialization**: Setting up the agent with models, tools, and configurations.
2. **State Graph Definition**: Creating and compiling a state graph with nodes (`start`, `directory_processor`, `document_file`, `readme_creator`) and conditional edges to manage transitions.
3. **Node Processing**: Implementing methods for each node to handle directory traversal, file documentation, and README creation.
4. **Documentation Generation**: Using models to generate commented code, summaries, and dependency trees.
5. **Logging and Event Streaming**: Logging actions and streaming events for frontend display.

The code is well-documented with docstrings and logging statements to facilitate understanding and maintenance.

**Internal Dependencies:** 
- prompts.py
- ../../tools/utils.py
- ../../utils/util.py
- ../agent.py
- ../../utils/logging.py
- state.py

### __init__.py
This file is currently empty and serves as an initializer for the module. It can be used to include any module-level initializations or imports in the future.

**Internal Dependencies:** None

### state.py
This file defines the `DocAgentState` class, which extends `AgentState` to manage the state of a documentation agent. This class includes attributes such as `entry_path`, `output_path`, `current_path`, `current_file`, `ignore_list`, `items_to_process`, `directory_structure`, `directory_stack`, `dependencies_per_file`, `legacy_language`, `legacy_framework`, and `indent`. These attributes help in tracking the documentation process, including paths, files, directories, dependencies, and formatting details.

**Internal Dependencies:** 
- ../state.py

## Getting Started

To get started with the `doc_agent` module, you can initialize the `DocAgent` class and use its methods to process and document your code directories and files. Make sure to configure the necessary models and tools as per your requirements.

## Contributing

We welcome contributions to improve the `doc_agent` module. Please ensure that your code is well-documented and includes appropriate tests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Thank you for using the `doc_agent` module! If you have any questions or need further assistance, feel free to reach out.