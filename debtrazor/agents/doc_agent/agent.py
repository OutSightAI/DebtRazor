import os
import json
from typing import Optional, Dict, List, Any
from pathlib import Path
from debtrazor.agents.agent import Agent
from langgraph.graph import StateGraph, END
from debtrazor.agents.doc_agent.prompts import (
    PROMPT,
    PROMPT_SUMMARY,
    PROMPT_README,
    PROMPT_DEPENDENCY_TREE,
)
from debtrazor.tools.utils import execute_tool
from debtrazor.agents.doc_agent.state import DocAgentState
from debtrazor.utils.logging import logger, add_to_log_queue
from debtrazor.constants import supported_langs, dependency_tool_supported_langs
from debtrazor.utils.util import is_ignored, parse_code_string, get_relative_path

# Constants
UNINITIALIZED_COUNT = -1
MAX_RECURSION_LIMIT = 1000


class DocAgent(Agent):
    def __init__(
        self, model, tools, checkpointer=None, thread_id: Optional[str] = None
    ):
        """
        Initialize the DocAgent with the given model, tools, checkpointer, and thread_id.

        Args:
            model: The model to be used by the agent.
            tools: The tools to be used by the agent.
            checkpointer: Optional checkpointer for state management.
            thread_id: Optional thread identifier.
        """
        super().__init__(model, tools)

        self.thread_id = f"{thread_id}_docAgent" if thread_id else None
        self.config = {"recursion_limit": MAX_RECURSION_LIMIT}

        if self.thread_id:
            self.config["configurable"] = {"thread_id": self.thread_id}

        # Defining the chains
        self.doc_chain = PROMPT | self.model
        self.summary_chain = PROMPT_SUMMARY | self.model
        self.readme_chain = PROMPT_README | self.model
        self.dependency_tree_chain = (
            PROMPT_DEPENDENCY_TREE.partial(
                tool_names=", ".join([tool.name for tool in tools])
            )
            | self.model.bind_tools(self.tools)
            | (lambda message: execute_tool(message, self.tools))
        )

        # Creating Agent graph
        logger.info("Creating Agent Graph")
        graph = StateGraph(DocAgentState)

        # Adding nodes
        graph.add_node("start", self.start_node)
        graph.add_node("directory_processor", self.directory_processor_node)
        graph.add_node("is_supported_code_file", self.is_supported_code_file_node)
        graph.add_node("document_file", self.document_file_node)
        graph.add_node("readme_creator", self.readme_creator_node)

        graph.set_entry_point("start")
        graph.add_edge("start", "directory_processor")

        # Adding edges
        graph.add_conditional_edges(
            "directory_processor",
            self.process_directory_or_file,
            {
                "start": "start",
                "is_supported_code_file": "is_supported_code_file",
                "readme_creator": "readme_creator",
                "end": END,
            },
        )
        graph.add_conditional_edges(
            "is_supported_code_file",
            self.continue_to_document_file_or_skip,
            {"document_file": "document_file", "start": "start"},
        )
        graph.add_conditional_edges(
            "document_file", self.should_continue, {"start": "start", "end": END}
        )
        graph.add_conditional_edges(
            "readme_creator", self.should_continue, {"start": "start", "end": END}
        )

        logger.debug(
            "Nodes: start, directory_processor, is_supported_code_file, "
            "document_file, readme_creator"
        )
        logger.debug("Conditional Edges: directory_processor")
        # Compiling graph
        self.graph = graph.compile(checkpointer=checkpointer.__enter__())

    def __call__(self, state: DocAgentState):
        """
        Execute the agent with the given state.

        Args:
            state (DocAgentState): The state to be processed by the agent.

        Returns:
            The result of the graph execution.
        """
        return self.graph.stream(state, config=self.config)

    def read_file(self, file_path: Path) -> str:
        """
        Reads the content of a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            str: The content of the file.
        """
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def add_documentation(self, code: str, language: str, framework: str) -> str:
        """
        Adds documentation to the code using the doc_chain.

        Args:
            code (str): The code to document.
            language (str): The programming language.
            framework (str): The framework used.

        Returns:
            str: The documented code.
        """
        response = self.doc_chain.invoke({
            "language": language,
            "framework": framework,
            "code_file": code,
        })
        return parse_code_string(response.content)

    def write_file(self, file_path: Path, content: str):
        """
        Writes content to a file.

        Args:
            file_path (Path): The path to the file.
            content (str): The content to write.
        """
        try:
            with file_path.open('w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Error writing to file {file_path}: {e}")
            raise

    def generate_summary_message(self, documented_code: str, language: str, framework: str, directory_path: str, file_name: str):
        """
        Generates a summary message for the documented code.

        Args:
            documented_code (str): The documented code.
            language (str): The programming language.
            framework (str): The framework used.
            directory_path (str): The directory path.
            file_name (str): The name of the file.

        Returns:
            Any: The summary message object.
        """
        response = self.summary_chain.invoke({
            "language": language,
            "framework": framework,
            "code_file": documented_code,
        })
        response.additional_kwargs["directory_path"] = directory_path
        response.additional_kwargs["file_name"] = file_name
        return response

    def extract_dependencies(self, file_path: Path, language: str, framework: str) -> Dict[str, Any]:
        """
        Extracts dependencies from the code file.

        Args:
            file_path (Path): The path to the code file.
            language (str): The programming language.
            framework (str): The framework used.

        Returns:
            Dict[str, Any]: A mapping of root to dependencies.
        """
        response = self.dependency_tree_chain.invoke({
            "language": language,
            "framework": framework,
            "code_file_path": str(file_path),
        })
        if hasattr(response, "dependencies"):
            return {response.root: response.dependencies}
        return {}

    def process_directory_or_file(self, state: DocAgentState) -> str:
        """
        Process the current directory or file based on the state.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            str: The next node to transition to.
        """
        current_path = state["current_path"]
        directory_stack = state["directory_stack"]
        items_to_process = state["items_to_process"]

        if current_path:
            path = Path(directory_stack[-1]["path"]) / current_path
            if path.is_dir():
                return "start"
            else:
                return "is_supported_code_file"

        if (
            (
                current_path is None
                and directory_stack[-1]["count"] == UNINITIALIZED_COUNT
            )
            or (
                current_path is None
                and directory_stack[-1]["count"] == 0
                and len(directory_stack) == 1
            )
            or (
                current_path is None
                and directory_stack[-1]["count"] == 0
                and not items_to_process
            )
        ):
            logger.debug("Transitioning to: readme_creator")
            return "readme_creator"
        else:
            logger.debug("Transitioning to: end")
            return "end"

    def should_continue(self, state: DocAgentState) -> str:
        """
        Determine whether the agent should continue processing.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            str: The next node to transition to.
        """
        if state["items_to_process"] and state["directory_stack"]:
            logger.debug("Continuing to: start")
            return "start"
        else:
            logger.debug("Transitioning to: end")
            return "end"

    def start_node(self, state: DocAgentState) -> Dict[str, Any]:
        """
        Start node of the agent's state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: The updated state.
        """
        current_path = state.get("current_path")
        items_to_process = state.get("items_to_process")
        directory_stack = state.get("directory_stack")
        directory_structure = state.get("directory_structure", "")
        indent = state.get("indent", "")

        logger.debug(f"Doc Agent on path: {current_path}")
        logger.debug(f"Items to process: {items_to_process}")

        # Determine the current directory path
        base_path = Path(directory_stack[-1]["path"])
        path = base_path / current_path if current_path else base_path

        if path.is_dir():
            # Avoid revisiting directories
            resolved_path = str(path.resolve())
            visited_paths = [d["path"] for d in directory_stack]
            if current_path and resolved_path not in visited_paths:
                directory_stack.append(
                    {
                        "path": resolved_path,
                        "count": UNINITIALIZED_COUNT,
                    }
                )

            # Initialize items in the directory if not already done
            if directory_stack[-1]["count"] == UNINITIALIZED_COUNT:
                try:
                    items = [item.name for item in path.iterdir()]
                    directory_stack[-1]["count"] = len(items)
                    items_to_process = items + (items_to_process or [])
                except Exception as e:
                    logger.error(f"Error listing directory {path}: {e}")
                    directory_stack[-1]["count"] = (
                        0  # Set count to 0 to avoid reprocessing
                    )

            # Update directory structure representation
            if current_path:
                is_not_last_item = directory_stack[-1]["count"] > 0
                prefix = "├── " if is_not_last_item else "└── "
                directory_structure += f"{indent}{prefix}{current_path}/\n"
                indent += "│   " if is_not_last_item else "    "

        updated_state = {
            "items_to_process": items_to_process,
            "current_path": current_path,
            "directory_structure": directory_structure,
            "indent": indent,
            "directory_stack": directory_stack,
        }
        return updated_state

    def directory_processor_node(self, state: DocAgentState) -> Dict[str, Any]:
        """
        Process the directory node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: The updated state.
        """
        items_to_process: List[str] = state.get("items_to_process", [])
        directory_stack: List[Dict[str, Any]] = state.get("directory_stack", [])
        indent: str = state.get("indent", "")
        ignore_list: List[str] = state.get("ignore_list", [])

        if items_to_process:
            while True:
                # Decrease the count of items in the current directory
                if directory_stack:
                    directory_stack[-1]["count"] -= 1

                    # If count reaches UNINITIALIZED_COUNT, we've processed all items
                    if directory_stack[-1]["count"] == UNINITIALIZED_COUNT:
                        indent = indent[:-4] if len(indent) >= 4 else ""
                        return {"current_path": None, "indent": indent}

                if not items_to_process:
                    # No more items to process
                    indent = indent[:-4] if len(indent) >= 4 else ""
                    return {"current_path": None, "indent": indent}

                next_item = items_to_process.pop(0)

                if not is_ignored(next_item, ignore_list):
                    # Found the next item to process
                    logger.debug(f"Next item to process: {next_item}")
                    return {"current_path": next_item, "indent": indent}

                # If the item is ignored, continue the loop to process next item

        else:
            return {"current_path": None, "indent": indent}

    def is_supported_code_file_node(self, state: DocAgentState) -> Dict[str, Any]:
        """
        Determine if the current file is a supported code file.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: The updated state.
        """
        current_path = state.get("current_path")
        legacy_language = state.get("legacy_language")

        if current_path:
            supported_extensions = supported_langs.get(legacy_language, [])
            file_extension = Path(current_path).suffix
            if file_extension in supported_extensions:
                logger.debug(f"File {current_path} is a supported code file.")
                return {"document_or_skip_current_file": True}
            else:
                logger.debug(f"File {current_path} is not a supported code file.")
        else:
            logger.debug("No current path to check for supported code file.")

        return {"document_or_skip_current_file": False}

    def continue_to_document_file_or_skip(self, state: DocAgentState) -> str:
        """
        Decide whether to document the current file or skip it.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            str: The next node to transition to.
        """
        if state.get("document_or_skip_current_file"):
            logger.debug("Continuing to document the file.")
            return "document_file"
        logger.debug("Skipping the file and returning to start.")
        return "start"

    def document_file_node(self, state: DocAgentState) -> Dict[str, Any]:
        """
        Process the document file node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: The updated state.
        """
        current_path = state.get("current_path")
        directory_stack = state.get("directory_stack", [])
        output_path = state.get("output_path")
        entry_path = state.get("entry_path")
        dependencies_per_file = state.get("dependencies_per_file", {})
        messages = state.get("messages", [])
        directory_structure = state.get("directory_structure", "")
        indent = state.get("indent", "")
        legacy_language = state.get("legacy_language")
        legacy_framework = state.get("legacy_framework")

        logger.info(f"Processing file: {current_path}")

        if not current_path:
            logger.error("No current path provided.")
            return {}

        # Construct the file path
        base_directory = Path(directory_stack[-1]["path"])
        file_path = base_directory / current_path

        try:
            # Read the code file
            code_file = self.read_file(file_path)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {}

        # Determine the relative output path
        relative_path = get_relative_path(str(base_directory), entry_path)
        output_directory = Path(output_path) / relative_path
        output_file_path = output_directory / current_path

        # Ensure the output directory exists
        output_directory.mkdir(parents=True, exist_ok=True)

        # Process and write the documented code
        try:
            documented_code = self.add_documentation(
                code_file, legacy_language, legacy_framework
            )
            self.write_file(output_file_path, documented_code)
        except Exception as e:
            logger.error(
                f"Failed to process and write documented code for {file_path}: {e}"
            )
            return {}

        # Generate summary and update messages
        try:
            summary_message = self.generate_summary_message(
                documented_code,
                legacy_language,
                legacy_framework,
                str(base_directory),
                current_path,
            )
            messages.append(summary_message)
        except Exception as e:
            logger.error(f"Failed to generate summary for {file_path}: {e}")

        # Extract dependencies if applicable
        if legacy_language in dependency_tool_supported_langs:
            try:
                dependencies = self.extract_dependencies(
                    file_path, legacy_language, legacy_framework
                )
                if dependencies:
                    dependencies_per_file.update(dependencies)
                    # Append dependencies to the summary message
                    dependencies_str = json.dumps(
                        dependencies[next(iter(dependencies))]
                    )
                    summary_message.content += (
                        f"\nInternal Dependencies: {dependencies_str}"
                    )
            except Exception as e:
                logger.error(f"Failed to extract dependencies for {file_path}: {e}")

        # Update the directory structure representation
        is_not_last_item = directory_stack[-1]["count"] > 0
        prefix = "├── " if is_not_last_item else "└── "
        directory_structure += f"{indent}{prefix}{current_path}\n"

        updated_state = {
            "directory_structure": directory_structure,
            "messages": messages,
            "dependencies_per_file": dependencies_per_file,
        }

        return updated_state

    def readme_creator_node(self, state: DocAgentState) -> Dict[str, Any]:
        """
        Process the README creator node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            Dict[str, Any]: The updated state.
        """
        # Ensure items_to_process is initialized
        items_to_process = state.get("items_to_process", [])
        state["items_to_process"] = items_to_process

        # Pop the last directory from the stack
        directory_stack = state.get("directory_stack", [])
        if not directory_stack:
            logger.error("Directory stack is empty. Cannot create README.")
            return {}

        current_directory = directory_stack.pop()
        directory_path = current_directory["path"]

        # Construct output paths
        entry_path = state.get("entry_path")
        output_path = state.get("output_path")
        relative_path = get_relative_path(directory_path, entry_path)
        output_directory_path = Path(output_path) / relative_path
        readme_file_path = output_directory_path / "README.md"

        # Generate summaries for files in the current directory
        messages = state.get("messages", [])
        file_summaries = [
            f"{msg.additional_kwargs['file_name']}: {msg.content}"
            for msg in messages
            if msg.additional_kwargs.get("directory_path") == directory_path
        ]
        file_summaries_text = "\n\n".join(file_summaries)

        # Generate README content
        module_name = Path(relative_path).name or "Root"
        readme_response = self.readme_chain.invoke(
            {
                "file_module_summaries": file_summaries_text,
                "module_name": module_name,
            }
        )

        # Write the README file
        output_directory_path.mkdir(parents=True, exist_ok=True)
        try:
            with readme_file_path.open("w", encoding="utf-8") as f:
                f.write(readme_response.content)
                logger.info("README.md file generated: %s", readme_file_path)
        except IOError as e:
            logger.error(f"Error writing README file at {readme_file_path}: {e}")

        # Remove processed messages
        remaining_messages = [
            msg
            for msg in messages
            if msg.additional_kwargs.get("directory_path") != directory_path
        ]
        state["messages"] = remaining_messages

        # Add the README message to messages
        if directory_stack:
            parent_directory_path = directory_stack[-1]["path"]
            readme_response.additional_kwargs["directory_path"] = parent_directory_path
            readme_response.additional_kwargs["file_name"] = Path(directory_path).name
        else:
            readme_response.additional_kwargs["directory_path"] = entry_path
            readme_response.additional_kwargs["file_name"] = "README.md"

        state["messages"].append(readme_response)

        # Update directory structure and indent
        indent = state.get("indent", "")
        if not items_to_process:
            state["directory_structure"] += f"{indent}└── README.md\n"
            state["indent"] = indent[:-4] if len(indent) >= 4 else ""
        else:
            state["directory_structure"] += f"{indent}│   └── README.md\n"

        updated_state = {
            "messages": state["messages"],
            "directory_structure": state["directory_structure"],
            "indent": state["indent"],
        }
        return updated_state

    @staticmethod
    async def stream_events(events: List[Dict[str, Any]], log_queue):
        """
        Stream events and add them to the log queue.

        Args:
            events (List[Dict[str, Any]]): The events to be streamed.
            log_queue: The log queue to add the events to.
        """
        for event in events:
            # Handle 'document_file' events
            if "document_file" in event:
                messages = event["document_file"].get("messages", [])
                if messages:
                    last_message = messages[-1]
                    file_name = last_message.additional_kwargs.get(
                        "file_name", "Unknown File"
                    )
                    content = last_message.content
                    log_message = f"{file_name}:\n{content}"
                    await add_to_log_queue(log_message, log_queue)
                else:
                    logger.warning("No messages found in 'document_file' event.")
            # Handle 'readme_creator' events
            elif "readme_creator" in event:
                messages = event["readme_creator"].get("messages", [])
                if messages:
                    content = messages[-1].content
                    await add_to_log_queue(content, log_queue)
                else:
                    logger.warning("No messages found in 'readme_creator' event.")
            else:
                logger.debug("Unhandled event type in stream_events.")
