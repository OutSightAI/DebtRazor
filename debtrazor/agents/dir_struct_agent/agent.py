from langgraph.prebuilt import ToolNode
from debtrazor.agents.agent import Agent
from langgraph.graph import StateGraph, START, END
from debtrazor.agents.dir_struct_agent.state import DirStructAgentState
from debtrazor.utils.logging import logger
from debtrazor.agents.dir_struct_agent.prompts import (
    PROMPT_DIR_STRUCT, 
    PROMPT_DIR_STRUCT_EXPERT_CRITIQUE, 
    EXTRACT_DIR_STRUCT_FILES_PROMPT
)
from debtrazor.schema.migrate import FilesToMigrate


class DirStructAgent(Agent):
    def __init__(self, model, tools, checkpointer=None, thread_id=None):
        super().__init__(model, tools)

        self.config = {}
        self.thread_id = thread_id + "_dirAgent"
        if self.thread_id is not None:
            self.config["configurable"] = {"thread_id": self.thread_id}

        self.dir_struct_chain = PROMPT_DIR_STRUCT.partial(
            tool_names=", ".join([tool.name for tool in tools])
        ) | self.model.bind_tools(self.tools)
        
        self.dir_struct_expert_critique = PROMPT_DIR_STRUCT_EXPERT_CRITIQUE | self.model
        
        self.extract_files_chain = EXTRACT_DIR_STRUCT_FILES_PROMPT | self.model.with_structured_output(FilesToMigrate)
        
        # Defining the tool node
        self.tool_node = ToolNode(tools)
        
        # Defining the graph
        logger.info("creating DirStructAgent graph")
        graph = StateGraph(DirStructAgentState)
        
        # Adding nodes and edges
        graph.add_node("dir_struct", self.dir_struct_node)
        graph.add_node("tool", self.tool_node)
        graph.add_node("critique", self.critique_node)
        graph.add_node("extract_files_to_migrate", self.extract_files_to_migrate)
        
        graph.add_edge(START, "dir_struct")
        graph.add_conditional_edges(
            "dir_struct", self.call_tool_or_critique, {True: "tool", False: "critique"}
        )
        graph.add_conditional_edges(
            "critique", self.call_dir_struct_or_end, {True: "dir_struct", False: "extract_files_to_migrate"}
        )
        graph.add_edge("tool", "dir_struct")
        graph.add_edge("extract_files_to_migrate", END)

        self.graph = graph.compile(checkpointer=checkpointer)
    
    def __call__(self, state: DirStructAgentState):
        return self.graph.invoke(state, config=self.config)
    
    def dir_struct_node(self, state: DirStructAgentState):
        logger.info("on node: dir_struct_node")
        response = self.dir_struct_chain.invoke({
            "legacy_language": state["legacy_language"], 
            "legacy_framework": state["legacy_framework"],
            "new_language": state["new_language"],
            "new_framework": state["new_framework"],
            "root_directory_path": state["entry_path"],
            "messages": state["messages"]
        })

        return {"messages": [response]}
    
    def call_tool_or_critique(self, state: DirStructAgentState):
        logger.info("on node: call_tool_or_critique")
        if len(state["messages"][-1].tool_calls) > 0:
            return True
        else:
            return False
        
    def critique_node(self, state: DirStructAgentState): 
        logger.info("on node: critique_node")
        response = self.dir_struct_expert_critique.invoke({
            "new_language": state["new_language"], 
            "new_framework": state["new_framework"], 
            "final_directory_structure": [state["messages"][-1]]
        })
        return {"messages": [response]}
    
    def call_dir_struct_or_end(self, state: DirStructAgentState): 
        if "END" in state["messages"][-1].content: 
            return False
        return True
    
    def extract_files_to_migrate(self, state: DirStructAgentState): 
        logger.info("on node: extract_file_to_migrate_node")
        
        response = self.extract_files_chain.invoke({
            "new_language": state["new_language"], 
            "new_framework": state["new_framework"],
            "new_directory_structure": state["messages"][-2].content
        })
        return {
            "files_to_migrate": response.files
        }