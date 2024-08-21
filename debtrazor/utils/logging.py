"""Global logging for the app"""

import asyncio
import logging
import sys


async def add_to_log_queue(message, log_queue):
    """
    Asynchronously add a message to the log queue.

    Args:
        message (str): The log message to be added to the queue.
        log_queue (asyncio.Queue): The queue to which the log message will be added.

    Returns:
        None
    """
    if log_queue:
        await log_queue.put(message)  # Put the message in the queue
        await asyncio.sleep(1)  # Simulate a delay


def setup_logger(name, level=logging.INFO):
    """
    Set up a logger with the given name and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
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
