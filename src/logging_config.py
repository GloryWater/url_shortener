"""Logging configuration for the application.

Provides structured JSON logging for production and readable console output for development.
"""

import logging
import sys
from datetime import datetime
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from src.config import Settings


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record["timestamp"] = datetime.utcnow().isoformat()

        # Add level name
        log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add location information
        log_record["location"] = f"{record.pathname}:{record.lineno}"

        # Add thread and process info
        log_record["thread"] = record.thread
        log_record["process"] = record.process

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_agent"):
            log_record["user_agent"] = record.user_agent
        if hasattr(record, "ip"):
            log_record["ip"] = record.ip


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for development."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(settings: Settings, is_production: bool = False) -> None:
    """Configure application logging.

    Args:
        settings: Application settings
        is_production: If True, use JSON format. Otherwise, use colored console output.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.app.debug else logging.INFO)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.app.debug else logging.INFO)

    if is_production:
        # JSON format for production
        formatter: logging.Formatter = CustomJsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        # Colored console format for development
        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific log levels for noisy libraries
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.database.sql_echo else logging.WARNING
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
