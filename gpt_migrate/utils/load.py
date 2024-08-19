import yaml
import asyncio
import argparse

from typing import Any
from gpt_migrate.utils.cfg import Config
from gpt_migrate.schema.request import AgentRequest
from gpt_migrate.utils.logging import add_to_log_queue


def load_config(config_path: str) -> dict[str, Any]:
    """Load and return the configuration from a YAML file."""
    with open(config_path, "r") as fp:
        return yaml.safe_load(fp)


def parse_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(description="Process a configuration file")
    parser.add_argument("config_path", help="Path to config file")
    return parser.parse_args()


async def load_and_validate_config(
    config_data: AgentRequest | None = None, log_queue: asyncio.Queue | None = None
):
    """Load configuration and validate essential parameters."""
    if config_data is None:
        args = parse_arguments()
        config_data = load_config(args.config_path)

    cfg = Config(config_data)

    # Validate essential configuration parameters
    if cfg.new_language is None:
        await add_to_log_queue(
            "ERROR: New language is required for migration", log_queue
        )
        raise ValueError("New language is required for migration")

    cfg.new_framework = cfg.new_framework or ""

    return cfg
