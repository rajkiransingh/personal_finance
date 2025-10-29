import logging
import os
import sys
from typing import Optional

import redis


class AppConfig:
    """Centralized configuration for the application"""
    _instance = None
    _redis_client = None

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
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

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
                retry_on_timeout=True
            )
            self._redis_client.ping()
        return self._redis_client

    def setup_logger(self, name: str) -> logging.Logger:
        """
        Set up a logger with both file and console handlers

        Args:
            name: Logger name (usually the module name)

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.LOG_LEVEL)
        return logger


# Single global instance
config = AppConfig()
