"""Logger configuration"""

import logging
import sys

import structlog


# Configure structlog with human-readable output
def setup_structlog() -> structlog.BoundLogger:
    """Initializes a structured logger"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.add_log_level,  # Add log level to log output
            structlog.processors.TimeStamper(fmt="iso"),  # Add timestamp in ISO format
            structlog.processors.StackInfoRenderer(),  # Include stack information if available
            structlog.processors.format_exc_info,  # Format exception info if an exception is logged
            structlog.dev.ConsoleRenderer(),  # Human-readable logs for development
        ],
        context_class=dict,  # Use dictionary to store log context
        logger_factory=structlog.stdlib.LoggerFactory(),  # Use stdlib logger factory
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO
        ),  # Set log level
        cache_logger_on_first_use=True,  # Cache loggers for better performance
    )

    # Set up basic configuration for the standard library logging
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.ERROR)

    # Return the structlog logger instance
    return structlog.get_logger()


# Initialize logger
logger = setup_structlog()
