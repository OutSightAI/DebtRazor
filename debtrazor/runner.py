import asyncio
from dotenv import load_dotenv
from debtrazor.migrate_utils.setup import (
    setup_memory,
    setup_environment,
    setup_initial_state,
    setup_initial_dir_struct_state,
    setup_initial_planner_state,
    setup_initial_migrate_state
)

from debtrazor.migrate_utils import (
    run_documentation_agent,
    run_dir_struct_agent,
    run_planner_agent,
    run_migrate_agent
)

from debtrazor.utils.cfg import Config

load_dotenv()

async def run_agent(cfg: Config, log_queue: asyncio.Queue | None = None):
    """
    Run the agent based on the configuration.

    Args:
        cfg (Config): Configuration object containing agent settings.
        log_queue (asyncio.Queue, optional): Queue for logging messages. Defaults to None.

    Returns:
        dict: The final state of the agent.
    """
   # Setup environment
    await setup_environment(cfg, log_queue=log_queue)

    # Setup long-term memory for the agents
    memory = setup_memory(cfg)

    # Create initial state
    init_state = setup_initial_state(cfg)

    # Run the documentation agent
    final_doc_state = await run_documentation_agent(init_state, memory, cfg, log_queue)

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
    
    
    init_migrate_state = setup_initial_migrate_state(
        cfg,
        documented_code_path=final_doc_state["output_path"],
        new_directory_structure=new_directory_structure,
        structured_migration_plan=final_planner_state["structured_migration_plan"]
    )
    
    run_migrate_agent(init_migrate_state, memory, cfg)
    
    # final_migrate_state = migrate_agent(migrate_agent_state)
    # use_statements = extract_all_dependencies(os.path.join(os.path.dirname(cfg.output_path), "target"))
    # use_statements = filter_dict_by_keys(use_statements, final_dir_struct_state["files_to_migrate"])
    
    import pdb;pdb.set_trace()