#!/usr/bin/env python3
"""
Configure uvicorn logging to use centralized logger.

Add this to your uvicorn start command or use this script to start the server.
"""

import uvicorn

# Import centralized config BEFORE starting uvicorn
from utilities.common.app_config import config


# Configure uvicorn's loggers to use our centralized logger
def configure_uvicorn_logging():
    """Configure uvicorn and FastAPI loggers to use centralized logging"""

    # Get our centralized logger configuration
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": config.CONSOLE_FORMAT,
                "datefmt": config.DATE_FORMAT,
            },
            "access": {
                "format": config.CONSOLE_FORMAT,
                "datefmt": config.DATE_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "default",
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": f"{config.LOG_DIR}/application.log",
                "when": "midnight",
                "interval": 30,
                "backupCount": 12,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    return log_config


if __name__ == "__main__":
    log_config = configure_uvicorn_logging()

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=log_config,
    )
