import asyncio
from dotenv import load_dotenv
from debtrazor.utils import load_and_validate_config

from debtrazor.migrate_utils.setup import (
    setup_environment,
    setup_initial_state,
    setup_memory,
)

from debtrazor.migrate_utils import (
    run_documentation_agent,
)


async def main():
    """
    Main function to orchestrate the code migration process.

    This function performs the following steps:
    1. Loads and validates the configuration.
    2. Sets up the environment based on the configuration.
    3. Sets up long-term memory for the agents.
    4. Creates the initial state for the migration.
    5. Runs the documentation agent.

    Returns:
        None
    """

    # Load and validate configuration
    cfg = await load_and_validate_config()

    # Setup environment
    await setup_environment(cfg, log_queue=None)

    # Setup long-term memory for the agents
    memory = setup_memory(cfg)

    # Create initial state
    init_state = setup_initial_state(cfg)

    # Run the documentation agent
    await run_documentation_agent(init_state, memory, cfg)


if __name__ == "__main__":
    _ = load_dotenv()  # Load environment variables from a .env file
    asyncio.run(main())  # Run the main function using asyncio
