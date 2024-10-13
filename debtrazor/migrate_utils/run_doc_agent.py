import asyncio
from debtrazor.migrate_utils.llm import get_llm
from debtrazor.agents.doc_agent.agent import DocAgent
from debtrazor.tools.tree.node_js import madge
from debtrazor.tools.tree.python import pydeps
from debtrazor.utils.logging import add_to_log_queue, logger
from debtrazor.tools.git.git_commit import push_changes_to_github


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

    logger.debug("Updated Current State: %s", current_state)

    if should_call_doc_agent:
        # Log and call the DocAgent to document the repository
        logger.info("Calling Doc agent to Document the repository")
        events = doc_agent(current_state)
        await DocAgent.stream_events(events, log_queue)
        result = doc_agent.graph.get_state(doc_agent.config).values
        if cfg.document.commit_to_git:
            # Commit the documentation changes to the repository
            await add_to_log_queue(
                "Committing documentation changes to the repository", log_queue
            )
            push_changes_to_github(
                cfg.entry_path, 
                current_state["output_path"], 
                cfg.github_token, 
                cfg.github_username, 
                cfg.repo_name, 
                cfg.document.doc_branch_name, 
                cfg.document.commit_message
            )
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
