import logging
import os
import sys
from typing import Optional

import redis


class AppConfig:
    """Centralized configuration for the application"""

    def __init__(self):
        # Environment variables with defaults
        self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # Logging configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_DIR = os.getenv("LOG_DIR", "./logs")
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Create logs directory
        os.makedirs(self.LOG_DIR, exist_ok=True)

        # Initialize Redis client (lazy loading)
        self._redis_client: Optional[redis.Redis] = None

    def redis_client(self) -> redis.Redis:
        """Get Redis client with lazy initialization"""
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(
                    host=self.REDIS_HOST,
                    port=self.REDIS_PORT,
                    db=self.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test the connection
                self._redis_client.ping()
            except redis.RedisError as e:
                logging.error(f"Failed to connect to Redis: {e}")
                raise
        return self._redis_client

    def setup_logger(self, name: str, log_file: Optional[str] = None) -> logging.Logger:
        """
        Set up a logger with both file and console handlers

        Args:
            name: Logger name (usually the module name)
            log_file: Optional custom log file name. If None, uses name-based naming

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Clear any existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Prevent propagation to root logger (this prevents duplicate messages)
        logger.propagate = False

        logger.setLevel(getattr(logging, self.LOG_LEVEL.upper()))

        # Create formatter
        formatter = logging.Formatter(self.LOG_FORMAT)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_file is None:
            log_file = f"{name.replace('.', '_')}_logs.log"

        log_path = os.path.join(self.LOG_DIR, log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger


# Global configuration instance
config = AppConfig()

# # Convenience functions for backward compatibility and ease of use
# def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
#     """Get a configured logger"""
#     return config.setup_logger(name, log_file)
#
#
# def get_redis_client() -> redis.Redis:
#     """Get Redis client"""
#     return config.redis_client
#
#
# def get_database_url() -> str:
#     """Get database URL"""
#     return config.DATABASE_URL
