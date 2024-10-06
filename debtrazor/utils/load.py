import yaml
import asyncio
import argparse

from typing import Any
from debtrazor.utils.cfg import Config
from debtrazor.schema.request import AgentRequest
from debtrazor.utils.logging import add_to_log_queue


def load_config(config_path: str) -> dict[str, Any]:
    """
    Load and return the configuration from a YAML file.

    Args:
        config_path (str): The path to the YAML configuration file.

    Returns:
        dict[str, Any]: The configuration data loaded from the YAML file.
    """
    with open(config_path, "r") as fp:
        return yaml.safe_load(fp)


# def parse_arguments() -> argparse.Namespace:
#     """
#     Parse and return command line arguments.

#     Returns:
#         argparse.Namespace: The parsed command line arguments.
#     """
#     parser = argparse.ArgumentParser(description="Process a configuration file")
#     parser.add_argument("config_path", help="Path to config file")
#     return parser.parse_args()

def parse_arguments() -> argparse.Namespace:
    """
    Parse and return command line arguments.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Process a configuration file")
    parser.add_argument("config_path", help="Path to config file")
    
    # Add --create-pull-request flag (defaults to False)
    parser.add_argument(
        "--create-pull-request", 
        action="store_true", 
        help="Flag to indicate if a pull request should be created. Default is False."
    )
    
    return parser.parse_args()



async def load_and_validate_config(
    config_data: AgentRequest | None = None, log_queue: asyncio.Queue | None = None
) -> Config:
    """
    Load configuration and validate essential parameters.

    Args:
        config_data (AgentRequest | None): The configuration data to validate. If None, it will be loaded from the config file.
        log_queue (asyncio.Queue | None): The queue to log errors. If None, logging will be skipped.

    Returns:
        Config: The validated configuration object.

    Raises:
        ValueError: If the new language is not specified in the configuration.
    """
    if config_data is None:
        # Parse command line arguments to get the config file path
        args = parse_arguments()
        # Load configuration from the specified file
        config_data = load_config(args.config_path)

    # Initialize the configuration object
    cfg = Config(config_data)

    # Validate essential configuration parameters
    if cfg.new_language is None:
        # Log an error if the new language is not specified
        await add_to_log_queue(
            "ERROR: New language is required for migration", log_queue
        )
        raise ValueError("New language is required for migration")

    # Set new framework to an empty string if it is not specified
    cfg.new_framework = cfg.new_framework or ""

    return cfg
