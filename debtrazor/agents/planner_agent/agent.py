from debtrazor.agents.agent import Agent
from debtrazor.utils.logging import logger
from langgraph.graph import StateGraph, START, END
from debtrazor.agents.planner_agent.state import PlannerAgentState
from debtrazor.schema.migrate import MigrationPlan
from debtrazor.agents.planner_agent.prompts import PLANNER_PROMPT, PLAN_EXTRACTOR_PROMPT


class PlannerAgent(Agent):
    def __init__(self, model, tools, checkpointer=None, thread_id=None):
        """
        Initialize the PlannerAgent with the given model, tools, checkpointer, and thread_id.

        Args:
            model: The model to be used by the agent.
            tools: The tools to be used by the agent.
            checkpointer: Optional checkpointer for state management.
            thread_id: Optional thread identifier.
        """
        super().__init__(model, tools)
        self.thread_id = thread_id + "_plannerAgent"
        self.config = {"recursion_limit": 1000}
        if self.thread_id is not None:
            self.config["configurable"] = {"thread_id": self.thread_id}

        self.planner_chain = PLANNER_PROMPT | self.model
        self.extract_structured_plan_chain = PLAN_EXTRACTOR_PROMPT | self.model.with_structured_output(MigrationPlan)
        

        # creating Agent graph
        logger.info("creating PlannerAgent graph")
        graph = StateGraph(PlannerAgentState)

        # Adding nodes and edges        
        graph.add_node("planner", self.planner_node)
        graph.add_node("extract_structured_plan", self.extract_structured_plan_node)

        graph.add_edge(START, "planner")
        graph.add_edge("planner", "extract_structured_plan")
        # graph.add_edge("planner", "update_planner")
        graph.add_edge("extract_structured_plan", END)
        

        self.graph = graph.compile(checkpointer=checkpointer)

    def __call__(self, state: PlannerAgentState):
        return self.graph.ainvoke(state, config=self.config)
    
    async def planner_node(self, state: PlannerAgentState):
        logger.info("on node: planner_node")
        response = await self.planner_chain.ainvoke({**state})
        return {
            "unstructured_migration_plan": response.content
        }
    
    async def extract_structured_plan_node(self, state: PlannerAgentState):
        logger.info("on node: extract_structured_plan")
        response = await self.extract_structured_plan_chain.ainvoke({
            "unstructured_migration_plan": state["unstructured_migration_plan"]
        })
        
        return {
            "structured_migration_plan": response
        }