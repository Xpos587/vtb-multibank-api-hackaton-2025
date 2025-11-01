import logging
import json
import sys
from datetime import datetime, timezone

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Formatter for structured JSON logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            exc_type = record.exc_info[0]
            log_entry["exception"] = {
                "type": exc_type.__name__ if exc_type else "Unknown",
                "message": str(record.exc_info[1]) if record.exc_info[1] else "No message",
            }

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging():
    """Configure the logging system."""
    # Set hardcoded format for all loggers
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # Get log level from settings
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    # Choose formatter based on environment
    if settings.is_production:
        formatter = StructuredFormatter()
    else:
        # Use hardcoded format instead of settings.logging.format
        formatter = logging.Formatter("[%(levelname)s] %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Configure third-party loggers
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("granian").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)


# Initialize logging when the module is imported
setup_logging()
