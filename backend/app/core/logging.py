"""Logging configuration for the Bidder backend."""
from __future__ import annotations

import logging
from logging.config import dictConfig
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / ".." / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def configure_logging(debug: bool = False) -> None:
    """Configure application logging.

    Parameters
    ----------
    debug:
        Whether to enable verbose logging output.
    """

    log_level = "DEBUG" if debug else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": log_level,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "standard",
                    "level": log_level,
                    "filename": str(LOG_DIR / "bidder.log"),
                    "maxBytes": 2 * 1024 * 1024,
                    "backupCount": 5,
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": log_level,
            },
        }
    )

    logging.getLogger(__name__).debug("Logging configured with level %s", log_level)
