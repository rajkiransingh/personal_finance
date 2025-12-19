import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

import redis
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AppConfig:
    """Centralized configuration for the application"""

    _instance = None
    _redis_client = None
    _loggers = {}  # Cache configured loggers

    def __new__(cls, *args, **kwargs):
        """Ensure AppConfig is a singleton"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        # Environment variables with defaults
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

        # DB URL
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # Logging configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_DIR = os.getenv("LOG_DIR", "./logs")

        # Standardized log formats
        # File format: More detailed with function names
        self.FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(funcName)-25s | %(message)s"
        # Console format: Simpler for Docker logs
        self.CONSOLE_FORMAT = (
            "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
        )
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

        # Create logs directory
        os.makedirs(self.LOG_DIR, exist_ok=True)

        # Initialize Redis client (lazy loading)
        self._redis_client: Optional[redis.Redis] = None

    def redis_client(self):
        """Singleton Redis client"""
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                db=self.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            self._redis_client.ping()
        return self._redis_client

    def setup_logger(self, name: str, level: str = None) -> logging.Logger:
        """
        Set up a logger with console and file handlers (dual output).

        Logs go to:
        1. Console (stdout) - INFO+ for Docker logs
        2. application.log - All levels (DEBUG+)
        3. error.log - Errors only (ERROR+)

        Files rotate monthly and keep 12 months of history.

        Args:
            name: Logger name (e.g., "api.routes.user", "utilities.stock_fetcher")
            level: Optional log level override (defaults to LOG_LEVEL from env)

        Returns:
            Configured logger instance
        """
        # Return cached logger if already configured
        if name in self._loggers:
            return self._loggers[name]

        logger = logging.getLogger(name)

        # Prevent duplicate handlers if logger already exists
        if logger.handlers:
            self._loggers[name] = logger
            return logger

        logger.setLevel(level or self.LOG_LEVEL)
        logger.propagate = False  # Don't propagate to root logger

        # 1. Console Handler (for Docker logs)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(self.CONSOLE_FORMAT, self.DATE_FORMAT)
        )
        console_handler.setLevel(logging.INFO)  # Only INFO+ to console
        logger.addHandler(console_handler)

        os.makedirs(self.LOG_DIR, exist_ok=True)
        # 2. Application Log File Handler (all levels)
        app_file_handler = TimedRotatingFileHandler(
            filename=os.path.join(self.LOG_DIR, "application.log"),
            when="midnight",
            interval=30,  # Rotate every 30 days (monthly)
            backupCount=12,  # Keep 12 months
            encoding="utf-8",
        )
        app_file_handler.setFormatter(
            logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)
        )
        app_file_handler.setLevel(logging.DEBUG)  # All levels to application.log
        app_file_handler.suffix = "%Y-%m"  # Archive naming: application.log.2025-01
        logger.addHandler(app_file_handler)

        # 3. Error Log File Handler (errors only)
        error_file_handler = TimedRotatingFileHandler(
            filename=os.path.join(self.LOG_DIR, "error.log"),
            when="midnight",
            interval=30,  # Rotate every 30 days (monthly)
            backupCount=12,  # Keep 12 months
            encoding="utf-8",
        )
        error_file_handler.setFormatter(
            logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)
        )
        error_file_handler.setLevel(logging.ERROR)  # Only ERROR+ to error.log
        error_file_handler.suffix = "%Y-%m"  # Archive naming: error.log.2025-01
        logger.addHandler(error_file_handler)

        # Cache the configured logger
        self._loggers[name] = logger

        return logger


# Single global instance
config = AppConfig()
