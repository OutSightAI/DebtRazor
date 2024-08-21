import os
import json
from debtrazor.agents.agent import Agent
from langgraph.graph import StateGraph, END
from debtrazor.agents.doc_agent.state import DocAgentState
from debtrazor.utils.util import is_ignored, parse_code_string, get_relative_path
from debtrazor.agents.doc_agent.prompts import (
    PROMPT,
    PROMPT_SUMMARY,
    PROMPT_README,
    PROMPT_DEPENDENCY_TREE,
)
from debtrazor.tools.utils import execute_tool
from debtrazor.utils.logging import logger, add_to_log_queue


class DocAgent(Agent):
    def __init__(self, model, tools, checkpointer=None, thread_id=None):
        """
        Initialize the DocAgent with the given model, tools, checkpointer, and thread_id.

        Args:
            model: The model to be used by the agent.
            tools: The tools to be used by the agent.
            checkpointer: Optional checkpointer for state management.
            thread_id: Optional thread identifier.
        """
        super().__init__(model, tools)

        self.thread_id = thread_id + "_docAgent"
        self.config = {"recursion_limit": 1000}
        if self.thread_id is not None:
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

        # creating Agent graph
        logger.info("Creating Agent Graph")
        graph = StateGraph(DocAgentState)

        # Adding nodes
        graph.add_node("start", self.start_node)
        graph.add_node("directory_processor", self.directory_processor_node)
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
                "document_file": "document_file",
                "readme_creator": "readme_creator",
                "end": END,
            },
        )
        graph.add_conditional_edges(
            "document_file", self.should_continue, {"start": "start", "end": END}
        )
        graph.add_conditional_edges(
            "readme_creator", self.should_continue, {"start": "start", "end": END}
        )

        logger.info(
            """Nodes: Start, directory_preprossor, document_file,
                     readme_creator"""
        )
        logger.info("Conditional Edges: directory_processor")
        # compiling graph
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

    def process_directory_or_file(self, state: DocAgentState):
        """
        Process the current directory or file based on the state.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            str: The next node to transition to.
        """
        logger.info("on node: process_directory_or_file")
        if state["current_path"] is not None:
            if os.path.isdir(
                os.path.join(
                    state["directory_stack"][-1]["path"], state["current_path"]
                )
            ):
                return "start"
            else:
                return "document_file"
        if (
            (
                state["current_path"] is None
                and state["directory_stack"][-1]["count"] == -1
            )
            or (
                state["current_path"] is None
                and state["directory_stack"][-1]["count"] == 0
                and len(state["directory_stack"]) == 1
            )
            or (
                state["current_path"] is None
                and state["directory_stack"][-1]["count"] == 0
                and len(state["items_to_process"]) == 0
            )
        ):
            logger.info("returned: readme_creator")
            return "readme_creator"
        else:
            logger.info("returned: end")
            return "end"

    def should_continue(self, state: DocAgentState):
        """
        Determine whether the agent should continue processing.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            str: The next node to transition to.
        """
        logger.info("on node: should_continue")
        if state["items_to_process"] is not None and len(state["directory_stack"]) != 0:
            logger.info("returned: start")
            return "start"
        else:
            logger.info("returned: end")
            return "end"

    def start_node(self, state: DocAgentState):
        """
        Start node of the agent's state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            dict: The updated state.
        """
        logger.info("on node: start_node")
        current_path = state["current_path"]

        items_to_process = state["items_to_process"]
        path = (
            os.path.join(state["directory_stack"][-1]["path"], current_path)
            if current_path is not None
            else state["directory_stack"][-1]["path"]
        )
        if os.path.isdir(path):
            if current_path is not None and os.path.join(
                state["directory_stack"][-1]["path"], state["current_path"]
            ) not in [d["path"] for d in state["directory_stack"]]:

                state["directory_stack"].append(
                    {
                        "path": os.path.join(
                            state["directory_stack"][-1]["path"], state["current_path"]
                        ),
                        "count": -1,
                    }
                )

            if state["directory_stack"][-1]["count"] == -1:
                items = os.listdir(path)
                state["directory_stack"][-1]["count"] = len(items)

                if items_to_process is None:
                    items_to_process = items
                else:
                    items_to_process = items + items_to_process

            if current_path is not None:
                prefix = (
                    "├── " if state["directory_stack"][-1]["count"] >= 0 else "└── "
                )

                state["directory_structure"] += (
                    state["indent"] + prefix + current_path + "/\n"
                )

                state["indent"] += (
                    "│   " if state["directory_stack"][-1]["count"] >= 0 else "    "
                )

        return {
            "items_to_process": items_to_process,
            "current_path": current_path,
            "directory_structure": state["directory_structure"],
            "indent": state["indent"],
        }

    def directory_processor_node(self, state: DocAgentState):
        """
        Process the directory node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            dict: The updated state.
        """
        logger.info("on node: director_processor_node")
        if state["items_to_process"]:
            while True:
                state["directory_stack"][-1]["count"] -= 1  # Decrease count
                if state["directory_stack"][-1]["count"] == -1:
                    state["indent"] = state["indent"][:-4]
                    return {"current_path": None, "indent": state["indent"]}
                next_item = state["items_to_process"].pop(0)
                if not is_ignored(next_item, state["ignore_list"]):
                    break
            return {"current_path": next_item}

        else:
            return {"current_path": None}

    def document_file_node(self, state: DocAgentState):
        """
        Process the document file node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            dict: The updated state.
        """
        logger.info("on node: document_file_node")
        logger.info(f"file name: {state['current_path']}")
        # TODO: Invoke the model to document the file.
        code_file = None
        message = None
        with open(
            os.path.join(state["directory_stack"][-1]["path"], state["current_path"]),
            "r",
        ) as f:
            code_file = f.read()

        relative_path = get_relative_path(
            state["directory_stack"][-1]["path"], state["entry_path"]
        )

        output_path = os.path.join(state["output_path"], relative_path)
        dependencies_per_file = state["dependencies_per_file"]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.exists(os.path.join(output_path, state["current_path"])):
            doc_commented_code_file = parse_code_string(
                self.doc_chain.invoke(
                    {
                        "language": state["legacy_language"],
                        "framework": state["legacy_framework"],
                        "code_file": code_file,
                    }
                ).content
            )

            try:
                with open(os.path.join(output_path, state["current_path"]), "w") as f:
                    f.write(doc_commented_code_file)
            except IOError:
                if os.path.exists(os.path.join(output_path, state["current_path"])):
                    os.remove(os.path.join(output_path, state["current_path"]))
                print("Error writing file")

            # pass doc_commented_code_file to the model again with the
            # summary chain to create a summary of the file and write the
            # summary along with the path to the messages in state
            code_file_summary = self.summary_chain.invoke(
                {
                    "language": state["legacy_language"],
                    "framework": state["legacy_framework"],
                    "code_file": doc_commented_code_file,
                }
            )
            code_file_summary.additional_kwargs["directory_path"] = state[
                "directory_stack"
            ][-1]["path"]
            code_file_summary.additional_kwargs["file_name"] = state["current_path"]
            message = code_file_summary

            dependency_tree = self.dependency_tree_chain.invoke(
                {
                    "language": state["legacy_language"],
                    "framework": state["legacy_framework"],
                    "code_file_path": os.path.join(
                        state["directory_stack"][-1]["path"], state["current_path"]
                    ),
                }
            )

            # from pdb import set_trace; set_trace()

            if hasattr(dependency_tree, "dependencies"):
                if (
                    len(dependency_tree.dependencies) > 0
                ):  # Check if the list is not empty
                    dependencies_str = json.dumps(dependency_tree.dependencies)
                else:  # Handle the empty list case
                    dependencies_str = json.dumps([])
                message.content += f"""\nInternal Dependencies: {dependencies_str}"""
            dependencies_per_file.update(
                {dependency_tree.root: dependency_tree.dependencies}
            )

        prefix = "├── " if state["directory_stack"][-1]["count"] >= 0 else "└── "
        state["directory_structure"] = (
            state["directory_structure"]
            + state["indent"]
            + prefix
            + state["current_path"]
            + "\n"
        )

        if message is not None:
            return {
                "directory_structure": state["directory_structure"],
                "messages": [message],
                "dependencies_per_file": dependencies_per_file,
            }

        return {
            "directory_structure": state["directory_structure"],
            "dependencies_per_file": dependencies_per_file,
        }

    def readme_creator_node(self, state: DocAgentState):
        """
        Process the README creator node in the state graph.

        Args:
            state (DocAgentState): The current state of the agent.

        Returns:
            dict: The updated state.
        """
        logger.info("on node: readme_creator_node")

        # Ensure items_to_process is initialized to an empty list if it's None
        if state["items_to_process"] is None:
            state["items_to_process"] = []

        # Pop the last directory from the stack
        directory_path = state["directory_stack"].pop(-1)["path"]

        # write this README.md in the output_path and add
        # the contents of README.md to the messages in state
        # with the path in the last position in the directory_stack
        # in state
        relative_path = get_relative_path(directory_path, state["entry_path"])
        output_directory_path = os.path.join(state["output_path"], relative_path)

        readme_file_path = os.path.join(output_directory_path, "README.md")

        # Generate the summaries and filter out the messages simultaneously
        file_or_module_summaries = [
            message.additional_kwargs["file_name"] + ":" + message.content + "\n\n"
            for message in state["messages"]
            if message.additional_kwargs["directory_path"] == directory_path
        ]

        file_or_module_summaries = "\n\n".join(file_or_module_summaries)

        readme = self.readme_chain.invoke(
            {
                "file_module_summaries": file_or_module_summaries,
                "module_name": os.path.basename(relative_path),
            }
        )

        try:
            with open(readme_file_path, "w") as f:
                f.write(readme.content)
        except IOError:
            print(f"Error writing README file at {readme_file_path}")

        # Filter the messages to exclude those that have been processed
        state["messages"] = [
            message
            for message in state["messages"]
            if message.additional_kwargs["directory_path"] != directory_path
        ]

        # Add the README.md path and content to the messages
        if len(state["directory_stack"]) > 0:
            readme.additional_kwargs["directory_path"] = state["directory_stack"][-1][
                "path"
            ]
            readme.additional_kwargs["file_name"] = os.path.basename(directory_path)
        else:
            readme.additional_kwargs["directory_path"] = state["entry_path"]
            readme.additional_kwargs["file_name"] = "README.md"

        # from pdb import set_trace; set_trace()

        if len(state["items_to_process"]) == 0:
            state["directory_structure"] += state["indent"] + "└── README.md\n"
            state["indent"] = state["indent"][:-4]
        else:
            state["directory_structure"] += state["indent"] + "│   " + "└── README.md\n"

        return {
            "messages": [readme],
            "directory_structure": state["directory_structure"],
            "indent": state["indent"],
        }

    @staticmethod
    async def stream_events(events, log_queue):
        """
        Stream events and add them to the log queue.

        Args:
            events: The events to be streamed.
            log_queue: The log queue to add the events to.
        """
        for event in events:
            # TODO: fix the logging here for showing information on the frontend
            if "document_file" in event.keys():
                await add_to_log_queue(
                    "\n".join(
                        [
                            f'{event["document_file"]["messages"][-1].additional_kwargs["file_name"]}:',
                            f'{event["document_file"]["messages"][-1].content}',
                        ]
                    ),
                    log_queue,
                )
            elif "readme_creator" in event.keys():
                await add_to_log_queue(
                    f'{event["readme_creator"]["messages"][-1].content}', log_queue
                )
