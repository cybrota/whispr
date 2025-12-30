"""Logger configuration"""

import logging
import os
import platform
from pathlib import Path
from datetime import datetime, timezone

import structlog


# Configure structlog with human-readable output
def _default_log_path() -> str:
    env_path = os.getenv("WHISPR_LOG_PATH")
    if env_path:
        return env_path

    if os.name == "nt":
        base_dir = os.getenv("PROGRAMDATA") or os.getenv("LOCALAPPDATA") or str(Path.home())
    else:
        base_dir = "/var/log"
    return str(Path(base_dir) / "whispr" / "access.log")


def _resolve_log_path() -> str:
    log_path = _default_log_path()
    log_dir = Path(log_path).parent
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_path
    except OSError:
        if platform.system() == "Darwin":
            fallback_dir = Path.home() / "Library" / "Logs" / "whispr"
        else:
            fallback_dir = Path.home() / ".local" / "state" / "whispr"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return str(fallback_dir / "access.log")


def setup_structlog() -> structlog.BoundLogger:
    """Initializes a structured logger"""
    log_path = _resolve_log_path()

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
    logging.basicConfig(format="%(message)s", handlers=[logging.FileHandler(log_path)], level=logging.INFO)

    # Return the structlog logger instance
    return structlog.get_logger()


# Initialize logger
logger = setup_structlog()


def log_secret_fetch(
    logger_instance: structlog.BoundLogger,
    secret_name: str,
    vault_type: str,
) -> None:
    """Log a fetched secret with a timezone-aware timestamp."""
    logger_instance.info(
        "Secret fetched",
        secret_name=secret_name,
        vault_type=vault_type,
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
