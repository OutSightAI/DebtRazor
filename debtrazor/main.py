import os
import asyncio
from dotenv import load_dotenv
from debtrazor.runner import run_agent as runAgent
from debtrazor.tools.git.git_commit import push_changes_to_github
from debtrazor.utils import load_and_validate_config
from debtrazor.utils.load import parse_arguments


# from debtrazor.agents.migrate_agent.agent import MigrateAgent
# from langchain_community.tools.file_management.read import ReadFileTool

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

    # await runAgent(cfg)

    args = parse_arguments()

    if args.create_pull_request:
        
        push_changes_to_github(cfg)

        # Add logic here to handle pull request creation
    else:
        print("Pull request will not be created.")


if __name__ == "__main__":
    _ = load_dotenv()  # Load environment variables from a .env file
    asyncio.run(main())  # Run the main function using asyncio
