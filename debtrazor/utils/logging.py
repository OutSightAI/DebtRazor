"""Global logging for the app"""

import asyncio
import logging
import sys


async def add_to_log_queue(message, log_queue):
    if log_queue:
        await log_queue.put(message)
        await asyncio.sleep(1)


def setup_logger(name, level=logging.INFO):
    """Set up a logger with the given name and level."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create a formatting for the logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


# Create a default logger for the entire application
logger = setup_logger("gpt_migrate")
