import os
import sqlite3
import asyncio
from debtrazor.utils.cfg import Config
from langchain.globals import set_verbose
from debtrazor.utils.util import read_gitignore
from langgraph.checkpoint.sqlite import SqliteSaver
from debtrazor.utils.logging import add_to_log_queue, logger
from debtrazor.agents.dir_struct_agent.prompts import DIR_STRUCT_PLAN_HUMAN_PROMPT


def setup_langchain_tracing(cfg: Config) -> None:
    """
    Set up langchain tracing based on configuration.

    Args:
        cfg (Config): Configuration object containing langchain tracing settings.

    Raises:
        ValueError: If project name is not provided when langchain tracing is enabled.
    """
    if cfg.langchain_tracing is not None:
        os.environ["LANGCHAIN_TRACING_V2"] = (
            "true" if cfg.langchain_tracing else "false"
        )

        if cfg.project_name is None:
            raise ValueError("Project name is required for tracing")
        else:
            os.environ["LANGCHAIN_PROJECT"] = cfg.project_name


async def setup_environment(cfg, log_queue: asyncio.Queue | None = None):
    """
    Setup the environment, including directories and logging.

    Args:
        cfg (Config): Configuration object containing environment settings.
        log_queue (asyncio.Queue, optional): Queue for logging messages. Defaults to None.

    Raises:
        PermissionError: If the output directory is not writable.
    """
    # Ensure output directory exists and is writable
    os.makedirs(cfg.output_path, exist_ok=True)
    if not os.access(cfg.output_path, os.W_OK):
        await add_to_log_queue(
            f"ERROR: No write permission for the directory: {cfg.output_path}",
            log_queue,
        )
        raise PermissionError(
            f"No write permission for the directory: {cfg.output_path}"
        )

    set_verbose(cfg.langchain_verbose)  # Set Langchain Verbosity
    setup_langchain_tracing(cfg)  # Setup langchain tracing


def setup_memory(cfg):
    """
    Setup memory using SqliteSaver.

    Args:
        cfg (Config): Configuration object containing memory settings.

    Returns:
        SqliteSaver: An instance of SqliteSaver initialized with the database path.
    """
    db_path = os.path.join(cfg.output_path, "checkpoint.db")
    logger.info("Database path: %s", db_path)
    
    # memory = SqliteSaver.from_conn_string(db_path)
    
    connection = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(connection)
    
    return memory


def setup_initial_state(cfg):
    """
    Create initial state for DocAgent if not already created.

    Args:
        cfg (Config): Configuration object containing initial state settings.

    Returns:
        dict: A dictionary representing the initial state.
    """
    init_state = {
        "entry_path": cfg.entry_path,
        "directory_stack": [{"path": cfg.entry_path, "count": -1}],
        "dependencies_per_file": {},
        "output_path": cfg.output_path,
        "legacy_language": cfg.legacy_language,
        "legacy_framework": cfg.legacy_framework,
        "ignore_list": read_gitignore(cfg.entry_path),
        "directory_structure": "",
        "indent": "",
        "current_path": None, 
        "items_to_process": [],
    }
    return init_state

def setup_initial_dir_struct_state(cfg, **kwargs): 
    try: 
        documented_code_path = kwargs["documented_code_path"]
        legacy_directory_structure = kwargs["legacy_directory_structure"]
    except KeyError:
        raise KeyError("documented_code_path and legacy_dircectory_structure must be provided in kwargs")

    init_dir_struct_state = {
        "entry_path": documented_code_path,
        "legacy_directory_structure": legacy_directory_structure,
        "legacy_language": cfg.legacy_language,
        "legacy_framework": cfg.legacy_framework, 
        "new_language": cfg.new_language,
        "new_framework": cfg.new_framework,
        "messages": [
            DIR_STRUCT_PLAN_HUMAN_PROMPT.format(
                directory_tree_structure=legacy_directory_structure,
                legacy_language=cfg.legacy_language, 
                legacy_framework=cfg.legacy_framework
            )
        ]
    }
    return init_dir_struct_state


def setup_initial_planner_state(cfg, **kwargs): 
    try:
        documented_code_path = kwargs["documented_code_path"]
        new_directory_structure = kwargs["new_directory_structure"]
        legacy_directory_structure = kwargs["legacy_directory_structure"]
        files_to_migrate = kwargs["files_to_migrate"]
        dependencies_per_file = kwargs["dependencies_per_file"]
    except KeyError:
        raise KeyError("new_directory_structure, documented_code_path, legacy_directory_structure, files_to_migrate, and dependencies_per_file must be provided in kwargs")
    
    init_planner_state = {
        "entry_path": documented_code_path,
        "legacy_language": cfg.legacy_language,
        "legacy_framework": cfg.legacy_framework,
        "new_language": cfg.new_language,
        "new_framework": cfg.new_framework,
        "new_directory_structure": new_directory_structure,
        "legacy_directory_structure": legacy_directory_structure,
        "files_to_migrate": files_to_migrate,
        "dependencies_per_file": dependencies_per_file, 
        "unstructured_migration_plan": "",
        "structured_migration_plan": None
    }
    
    return init_planner_state


def setup_initial_migrate_state(cfg, **kwargs): 
    try:
        documented_code_path = kwargs["documented_code_path"]
        new_directory_structure = kwargs["new_directory_structure"]
        structured_migration_plan = kwargs["structured_migration_plan"]
    except KeyError:
        raise KeyError("new_directory_structure, structured_migration_plan, and documented_code_path must be provided in kwargs")
    
    init_migrate_state = {
        "entry_path": documented_code_path,
        "output_path": os.path.join(os.path.dirname(cfg.output_path), "target"),
        "legacy_language": cfg.legacy_language,
        "new_language": cfg.new_language,
        "new_directory_structure": new_directory_structure,
    }
    
    return init_migrate_state, structured_migration_plan