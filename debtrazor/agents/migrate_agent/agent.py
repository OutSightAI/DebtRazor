from langgraph.prebuilt import ToolNode
from debtrazor.agents.agent import Agent
from debtrazor.utils.logging import logger
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from debtrazor.agents.migrate_agent.prompts import (
    FILE_MIGRATION_PLANNER_PROMPT,
    FILE_MIGRATION_PROMPT,
    WRITER_PROMPT
)
from debtrazor.tools.file_management.write import WriteFileTool
from debtrazor.agents.migrate_agent.state import MigrateAgentState


class MigrateAgent(Agent): 
    def __init__(self, model, tools, checkpointer=None, thread_id=None): 
        super().__init__(model, tools)

        self.config = {}
        self.thread_id = thread_id + "_MigrationAgent"
        if self.thread_id is not None:
            self.config["configurable"] = {"thread_id": self.thread_id}
        
        self.file_migration_planner_chain = FILE_MIGRATION_PLANNER_PROMPT | model
        self.file_migration_chain = FILE_MIGRATION_PROMPT.partial(
            tool_names=", ".join([tool.name for tool in tools])
        ) | model.bind_tools(tools)

        writing_tools = [WriteFileTool()]
        self.writer_chain = WRITER_PROMPT.partial(
            tool_names=", ".join([tool.name for tool in writing_tools])
        ) | model.bind_tools(writing_tools) 
        
        # Defining the graph
        self.tool_node = ToolNode(tools)
        self.writing_tool_node = ToolNode(writing_tools)

        graph = StateGraph(MigrateAgentState)

        # Adding nodes and edges
        graph.add_node("file_migration_planner", self.file_migration_planner_node)
        graph.add_node("migrate", self.file_migration_node)
        graph.add_node("tool", self.tool_node)
        graph.add_node("write_file_node", self.write_file_node)
        graph.add_node("writing_tool_node", self.writing_tool_node)
        graph.add_node("end_node", self.end_node)

        graph.add_edge(START, "file_migration_planner")
        graph.add_edge("file_migration_planner", "migrate")
        graph.add_edge("tool", "migrate")
        graph.add_edge("end_node", END)
        graph.add_edge("writing_tool_node", "end_node")

        graph.add_conditional_edges(
            "migrate", 
            self.call_tool_or_end, 
            {
                True: "tool", 
                False: "write_file_node"
            }
        )
        graph.add_conditional_edges(
            "write_file_node", 
            self.call_tool_or_end, 
            {
                True: "writing_tool_node", 
                False: "end_node"
            }
        )
        
        self.graph = graph.compile(checkpointer=checkpointer)

    def __call__(self, state: MigrateAgentState):
        return self.graph.invoke(state, config=self.config)
    
    def file_migration_planner_node(self, state: MigrateAgentState):
        logger.info("on node: migration_file_planner")
        
        response = self.file_migration_planner_chain.invoke({
            "legacy_language": state["legacy_language"],
            "new_language": state["new_language"],
            "new_directory_structure": state["new_directory_structure"],
            "file_to_migrate": state["file_to_migrate"].file_name,
            "file_description": state["file_to_migrate"].description,
            "legacy_incontext_files": state["file_to_migrate"].legacy_context,
            "target_incontext_files": state["file_to_migrate"].new_context,
        })
        
        return {
            "current_plan": response.content
        }
    
    def file_migration_node(self, state: MigrateAgentState):
        logger.info("on node: migrate")
        
        last_message_with_end_index = next((i for i in range(len(state["messages"]) - 1, -1, -1) if "END" in state["messages"][i].content), -1)

        response = self.file_migration_chain.invoke({
            "legacy_language": state["legacy_language"],
            "new_language": state["new_language"],
            "input_directory_path": state["entry_path"],
            "output_directory_path": state["output_path"],
            "file_migration_plan": state["current_plan"],
            "file_to_migrate": state["file_to_migrate"].file_name,
            "legacy_incontext_files": state["file_to_migrate"].legacy_context,
            "target_incontext_files": state["file_to_migrate"].new_context,
            "messages": state["messages"][last_message_with_end_index + 1:]
        })

        return {
            "messages": [response]
        }
        
    def write_file_node(self, state: MigrateAgentState):
        logger.info("on node: write_file_node")
        response = self.writer_chain.invoke({      
            "new_language": state["new_language"],
            "output_directory_path": state["output_path"],
            "file_to_migrate": state["file_to_migrate"].file_name,
            "message_to_extract_code_from": state["messages"][-1].content
        })
        
        return {
            "messages": [response]
        }

    def end_node(self, state: MigrateAgentState):
        logger.info("on node: end_node")
        
        return {
            "messages": [AIMessage(content="END")]
        }

    def call_tool_or_end(self, state: MigrateAgentState):
        logger.info("on node: call_tool_or_end")
        if len(state["messages"][-1].tool_calls) > 0:
            return True
        else:
            return False