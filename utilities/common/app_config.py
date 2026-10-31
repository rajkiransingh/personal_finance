import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

import redis
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Logger name prefix → log category (subdirectory/basename) mapping.
# A logger whose name *starts with* a key is routed to that category's files.
# Evaluated in order; the first match wins.
# ---------------------------------------------------------------------------
_LOG_CATEGORIES = [
    # API / backend routes
    ("api.",                                "backend/api"),
    ("backend.",                            "backend/api"),
    # Scheduled fetcher scripts
    ("scripts.",                            "scheduler/scheduler"),
    # Individual data fetchers
    ("utilities.forex_fetcher",             "fetchers/fetchers"),
    ("utilities.stock_fetcher",             "fetchers/fetchers"),
    ("utilities.crypto_fetcher",            "fetchers/fetchers"),
    ("utilities.metal_fetcher",             "fetchers/fetchers"),
    ("utilities.mutual_fund_fetcher",       "fetchers/fetchers"),
    # Analytics & dashboard
    ("utilities.dashboard",                 "analytics/analytics"),
    ("utilities.analytics",                 "analytics/analytics"),
    # Fallback — anything unmatched goes to backend/api
    ("",                                    "backend/api"),
]


def _resolve_log_category(name: str) -> str:
    """Return the log category path (relative to LOG_DIR) for a logger name."""
    for prefix, category in _LOG_CATEGORIES:
        if name.startswith(prefix):
            return category
    return "backend/api"


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
        # Use an absolute path so logs always land in the same place regardless
        # of which process or working directory calls setup_logger().
        # Inside Docker the default is /app/logs (mounted to ./logs/ on host).
        # Override with LOG_DIR env var for local dev or tests.
        self.LOG_DIR = os.getenv("LOG_DIR", "/app/logs")

        # Integration Configuration
        self.RAIDEN_URL = os.getenv("RAIDEN_URL", "http://raiden:8000")
        self.N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
        self.SERVICE_NAME = os.getenv("SERVICE_NAME", "Financer")

        # Standardized log formats
        # File format: More detailed with function names
        self.FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(funcName)-25s | %(message)s"
        # Console format: Simpler for Docker logs
        self.CONSOLE_FORMAT = (
            "%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s"
        )
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

        # Create base logs directory (subdirectories are created in setup_logger)
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
        Set up a category-aware logger with console and file handlers.

        Each logger is routed to a dedicated subdirectory under LOG_DIR based
        on its name prefix (see _LOG_CATEGORIES at the top of this module):

            logs/
            ├── backend/
            │   ├── api.log          ← api.*, backend.* loggers
            │   └── api.error.log    ← ERROR+ from API
            ├── scheduler/
            │   ├── scheduler.log    ← scripts.* loggers
            │   └── scheduler.error.log
            ├── fetchers/
            │   ├── fetchers.log     ← utilities.*_fetcher loggers
            │   └── fetchers.error.log
            ├── analytics/
            │   ├── analytics.log    ← utilities.dashboard.*, utilities.analytics.*
            │   └── analytics.error.log
            └── app.error.log        ← Master: ALL errors from ALL loggers (ELK feed)

        Files rotate monthly (30-day interval) and keep 12 months of history.

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

        # Resolve the category subdirectory/basename for this logger
        category = _resolve_log_category(name)  # e.g. "backend/api"
        category_dir = os.path.join(self.LOG_DIR, os.path.dirname(category))
        category_base = os.path.basename(category)  # e.g. "api"
        os.makedirs(category_dir, exist_ok=True)

        # Shared formatter helper
        file_fmt = logging.Formatter(self.FILE_FORMAT, self.DATE_FORMAT)

        def _make_rotating_handler(filepath: str, min_level: int) -> TimedRotatingFileHandler:
            h = TimedRotatingFileHandler(
                filename=filepath,
                when="midnight",
                interval=30,   # Rotate every 30 days (monthly)
                backupCount=12,  # Keep 12 months of archives
                encoding="utf-8",
            )
            h.setFormatter(file_fmt)
            h.setLevel(min_level)
            h.suffix = "%Y-%m"  # Archive naming: api.log.2025-01
            return h

        # 1. Console handler — INFO+ for Docker logs / stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(self.CONSOLE_FORMAT, self.DATE_FORMAT)
        )
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # 2. Category application log — all levels (DEBUG+)
        category_log = os.path.join(category_dir, f"{category_base}.log")
        logger.addHandler(_make_rotating_handler(category_log, logging.DEBUG))

        # 3. Category error log — ERROR+ only, per-category
        category_err = os.path.join(category_dir, f"{category_base}.error.log")
        logger.addHandler(_make_rotating_handler(category_err, logging.ERROR))

        # 4. Master error log — ERROR+ from ALL loggers, one file for ELK ingest
        master_err = os.path.join(self.LOG_DIR, "app.error.log")
        logger.addHandler(_make_rotating_handler(master_err, logging.ERROR))

        # Cache the configured logger
        self._loggers[name] = logger

        return logger


# Single global instance
config = AppConfig()
