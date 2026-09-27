import logging
import sys
import json
from datetime import datetime, timezone


class CustomJsonFormatter(logging.Formatter):
    """Formats log records as structured JSON for fluent-bit / promtail ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "aiops-backend",
        }

        # Include exception info if available
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include custom extra fields if provided
        for key, val in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread",
                "threadName"
            ):
                log_entry[key] = val

        return json.dumps(log_entry)


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """Configures and returns the root application logger."""
    logger = logging.getLogger("aiops")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if setup is invoked multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(CustomJsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = setup_logger()
