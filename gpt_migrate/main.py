import asyncio
from dotenv import load_dotenv
from gpt_migrate.utils import load_and_validate_config


from gpt_migrate.migrate_utils.setup import (
    setup_environment,
    setup_initial_state,
    setup_memory,
)

from gpt_migrate.migrate_utils import (
    run_documentation_agent,
)


async def main():
    """
    Main function to orchestrate the code migration process.
    """

    # Load and validate configuration
    cfg = await load_and_validate_config()

    # Setup environment
    await setup_environment(cfg, log_queue=None)

    # long term memory for the agents
    init_state = setup_memory(cfg)

    # Crete Init State
    memory = setup_initial_state(cfg)

    # Documentation Agent
    await run_documentation_agent(init_state, memory, cfg)


if __name__ == "__main__":
    _ = load_dotenv()  # Load Environment Variables
    asyncio.run(main())  # Run the Main Function
