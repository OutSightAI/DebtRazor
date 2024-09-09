import asyncio
from dotenv import load_dotenv
from debtrazor.utils import load_and_validate_config

from debtrazor.migrate_utils.setup import (
    setup_memory,
    setup_environment,
    setup_initial_state,
    setup_initial_dir_struct_state,
    setup_initial_planner_state,
)

from debtrazor.migrate_utils import (
    run_documentation_agent,
    run_dir_struct_agent,
    run_planner_agent
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
    final_doc_state = await run_documentation_agent(init_state, memory, cfg)

    # Get the initial directory structure state
    init_dir_struct_state = setup_initial_dir_struct_state(
        cfg, 
        documented_code_path=final_doc_state["output_path"], 
        legacy_directory_structure=final_doc_state["directory_structure"]
    )
    
    # Run the directory structure agent
    final_dir_struct_state = run_dir_struct_agent(init_dir_struct_state, memory, cfg)
    
    new_directory_structure = final_dir_struct_state["messages"][-2].content
    
    init_planner_state = setup_initial_planner_state(
        cfg,
        documented_code_path=final_doc_state["output_path"],
        new_directory_structure=new_directory_structure, 
        legacy_directory_structure=final_doc_state["directory_structure"],
        files_to_migrate=final_dir_struct_state["files_to_migrate"],
        dependencies_per_file=final_doc_state["dependencies_per_file"]
    )
    
    # Run the planner agent
    final_planner_state = run_planner_agent(init_planner_state, memory, cfg)
    
    #import pdb;pdb.set_trace()
    
if __name__ == "__main__":
    _ = load_dotenv()  # Load environment variables from a .env file
    asyncio.run(main())  # Run the main function using asyncio
