import asyncio
from debtrazor.tools.tree.python import pydeps
from debtrazor.tools.tree.node_js import madge
from debtrazor.migrate_utils.llm import get_llm
from debtrazor.agents.doc_agent.agent import DocAgent
from debtrazor.utils.logging import add_to_log_queue, logger
from debtrazor.agents.planner_agent.agent import PlannerAgent
from debtrazor.agents.dir_struct_agent.agent import DirStructAgent
from debtrazor.agents.migrate_agent.agent import MigrateAgent
from langchain_community.tools.file_management.read import ReadFileTool


async def run_documentation_agent(
    init_state, memory, cfg, log_queue: asyncio.Queue | None = None
):
    """
    Process documentation using DocAgent.

    This function initializes and runs the DocAgent to process documentation
    for a repository. It checks the current state of the documentation process
    and decides whether to call the DocAgent to continue or finalize the
    documentation.

    Args:
        init_state: The initial state of the documentation process.
        memory: The memory object used for checkpointing.
        cfg: Configuration object containing settings for the DocAgent.
        log_queue (asyncio.Queue | None): Optional queue for logging messages.

    Returns:
        dict: The final state of the documentation process.
    """

    # Initialize the documentation model and agent
    doc_model = get_llm(cfg.document.model)
    doc_agent = DocAgent(
        doc_model, [madge, pydeps], checkpointer=memory, thread_id=str(cfg.thread_id)
    )

    # Get the current state of the documentation process
    current_state = doc_agent.graph.get_state(doc_agent.config)

    # Determine if the agent is running for the first time
    if current_state.created_at is None:  # Agent is running for the first time
        current_state = init_state
        should_call_doc_agent = True
    else:  # Agent has run before
        current_state = current_state.values
        should_call_doc_agent = bool(
            current_state.get("items_to_process")
        )  # If there are items remaining to process i.e. agent ran partially

    logger.info("Updated Current State: %s", current_state)

    if should_call_doc_agent:
        # Log and call the DocAgent to document the repository
        await add_to_log_queue(
            "Calling Doc agent to Document the repository", log_queue
        )
        logger.info("Calling Doc Agent")
        events = doc_agent(current_state)
        await DocAgent.stream_events(events, log_queue)
        result = doc_agent.graph.get_state(doc_agent.config).values
    else:
        # Log that the documentation process is already complete
        await add_to_log_queue(
            " ".join(
                [
                    "The document agent has already finalized documenting the",
                    " repository. Skipping the document agent execution.",
                ]
            ),
            log_queue,
        )
        result = current_state

    logger.info("DocAgent Result: %s", result)
    return result


def run_dir_struct_agent(init_state, memory, cfg, log_queue: asyncio.Queue | None = None):
    dir_struct_model = get_llm(cfg.dir_struct.model)
    dir_struct_agent = DirStructAgent(
        dir_struct_model, [ReadFileTool()], checkpointer=memory, thread_id=str(cfg.thread_id)
    )
    
    should_call_dir_struct_agent = False
    current_state = dir_struct_agent.graph.get_state(dir_struct_agent.config)
    
    # Determine if the agent is running for the first time
    if current_state.created_at is None or len(current_state.values["messages"]) == 0:  # Agent is running for the first time
        current_state = init_state
        should_call_dir_struct_agent = True
    else: 
        current_state = current_state.values
    logger.info("Updated Current State: %s", current_state)

    if should_call_dir_struct_agent:
        logger.info("Calling dir struct Agent")
        result = dir_struct_agent(current_state)
    else: 
        result = current_state
    
    logger.info("DirStructAgent Result: %s", result)
    return result


def run_planner_agent(init_state, memory, cfg, log_queue: asyncio.Queue | None = None):
    planner_model = get_llm(cfg.planner.model)
    planner_agent = PlannerAgent(
        planner_model, [], checkpointer=memory, thread_id=str(cfg.thread_id)
    )
    
    should_call_planner_agent = False
    current_state = planner_agent.graph.get_state(planner_agent.config)
    
    # Determine if the agent is running for the first time
    if current_state.created_at is None or current_state.values["structured_migration_plan"] is None:  # Agent is running for the first time
        current_state = init_state
        should_call_planner_agent = True
    else: 
        current_state = current_state.values
    logger.info("Updated Current State: %s", current_state)

    if should_call_planner_agent:
        logger.info("Calling planner Agent")
        result = planner_agent(current_state)
    else: 
        result = current_state
    
    logger.info("PlannerAgent Result: %s", result)
    return result


def run_migrate_agent(init_state, memory, cfg, log_queue: asyncio.Queue | None = None):
    migrate_model = get_llm(cfg.migrate.model)
    
    migrate_agent = MigrateAgent(
        migrate_model, [ReadFileTool()], checkpointer=memory, thread_id=str(cfg.thread_id)
    )
    init_state, structured_migration_plan = init_state

    for i in range(len(structured_migration_plan.steps)):
        init_state["file_to_migrate"] = structured_migration_plan.steps[i]
        logger.info("Calling migrate Agent for file %s", structured_migration_plan.steps[i].file_name)
        migrate_agent(init_state)
    
