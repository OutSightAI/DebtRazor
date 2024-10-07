import os
import asyncio
from debtrazor.utils.cfg import Config
from langchain.globals import set_verbose
from debtrazor.utils.logging import add_to_log_queue, logger
from debtrazor.utils.util import read_gitignore
from langgraph.checkpoint.sqlite import SqliteSaver


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
    memory = SqliteSaver.from_conn_string(db_path)
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
        "output_path": os.path.join(cfg.output_path, cfg.legacy_language),
        "legacy_language": cfg.legacy_language,
        "legacy_framework": cfg.legacy_framework,
        "ignore_list": read_gitignore(cfg.entry_path),
        "directory_structure": "",
        "indent": "",
        "current_path": None,
        "items_to_process": [],
    }
    return init_state
