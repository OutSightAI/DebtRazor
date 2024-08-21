import asyncio
from debtrazor.migrate_utils.llm import get_llm
from debtrazor.utils.logging import add_to_log_queue, logger
from debtrazor.agents.doc_agent.agent import DocAgent
from debtrazor.tools.tree.node_js import madge
from debtrazor.tools.tree.python import pydeps


async def run_documentation_agent(
    init_state, memory, cfg, log_queue: asyncio.Queue | None = None
):
    """Process documentation using DocAgent."""

    doc_model = get_llm(cfg.document.model)
    doc_agent = DocAgent(
        doc_model, [madge, pydeps], checkpointer=memory, thread_id=str(cfg.thread_id)
    )

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
        await add_to_log_queue(
            "Calling Doc agent to Document the repository", log_queue
        )
        logger.info("Calling Doc Agent")
        events = doc_agent(current_state)
        await DocAgent.stream_events(events, log_queue)
        result = doc_agent.graph.get_state(doc_agent.config).values
    else:
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
