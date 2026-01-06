#!/usr/bin/env python3
"""
Environment Variable Validation Script for Personal Finance Application

This script validates that all required environment variables are properly set
and provides helpful error messages for any issues found.
"""

import os
import sys
from typing import List, Tuple

from dotenv import load_dotenv


class Color:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(message: str):
    """Print a formatted header"""
    print(f"\n{Color.BLUE}{Color.BOLD}{'=' * 70}{Color.END}")
    print(f"{Color.BLUE}{Color.BOLD}{message.center(70)}{Color.END}")
    print(f"{Color.BLUE}{Color.BOLD}{'=' * 70}{Color.END}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Color.GREEN}✓ {message}{Color.END}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Color.YELLOW}⚠ {message}{Color.END}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Color.RED}✗ {message}{Color.END}")


def check_env_file() -> bool:
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print_error(".env file not found!")
        print_warning("Please copy .env.example to .env and configure it:")
        print(f"  {Color.BOLD}cp .env.example .env{Color.END}")
        return False
    print_success(".env file found")
    return True


def validate_required_vars() -> Tuple[List[str], List[str]]:
    """
    Validate required environment variables
    Returns: (missing_vars, invalid_vars)
    """
    required_vars = {
        "MYSQL_ROOT_PASSWORD": "MySQL root password",
        "MYSQL_DATABASE": "MySQL database name",
        "MYSQL_USER": "MySQL username",
        "MYSQL_PASSWORD": "MySQL user password",
        "DATABASE_URL": "Database connection URL",
        "EXCHANGE_RATE_API_KEY": "Exchange rate API key",
        "RAPID_API_MF_HOST": "RapidAPI host for mutual funds",
        "RAPID_MF_API_KEY": "Key for mutual fund API",
        "RAPID_API_BULLION_HOST": "RapidAPI Bullion host",
        "RAPID_API_KEY": "RapidAPI API key",
        "COIN_MARKET_URL": "Coin Market URL",
        "COIN_MARKET_CAP_API_KEY": "Coin Market API key",
    }

    missing = []
    invalid = []

    for var, description in required_vars.items():
        value = os.getenv(var)

        if not value:
            missing.append(f"{var} ({description})")
            print_error(f"Missing: {var} - {description}")
        elif value.startswith("your_") or value.endswith("_here"):
            invalid.append(f"{var} ({description})")
            print_warning(f"Not configured: {var} - still using placeholder value")
        else:
            print_success(f"{var} - configured")

    return missing, invalid


def validate_optional_vars():
    """Validate optional environment variables and show defaults"""
    optional_vars = {
        "REDIS_HOST": ("redis", "Redis hostname"),
        "REDIS_PORT": ("6379", "Redis port"),
        "REDIS_DB": ("0", "Redis database number"),
        "LOG_LEVEL": ("INFO", "Logging level"),
        "LOG_DIR": ("./logs", "Log directory"),
        "NSE_WEBSITE_URL": ("https://www.nseindia.com", "NSE website URL"),
    }

    print(f"\n{Color.BOLD}Optional Variables (using defaults if not set):{Color.END}")
    for var, (default, description) in optional_vars.items():
        value = os.getenv(var, default)
        if os.getenv(var):
            print_success(f"{var} = {value} ({description})")
        else:
            print(f"  {var} = {value} ({description}) [default]")


def validate_database_url():
    """Validate DATABASE_URL format"""
    db_url = os.getenv("DATABASE_URL", "")

    if not db_url:
        return

    # Check if it matches expected format
    if not db_url.startswith("mysql+pymysql://"):
        print_warning("DATABASE_URL should start with 'mysql+pymysql://'")
        return

    # Extract components for validation
    try:
        # Basic format check
        if "@" not in db_url or ":" not in db_url:
            print_warning("DATABASE_URL format may be incorrect")
            print(
                "Expected format: mysql+pymysql://username:password@host:port/database"
            )
            return

        print_success("DATABASE_URL format looks valid")
    except Exception as e:
        print_warning(f"Could not validate DATABASE_URL format: {e}")


def check_api_keys():
    """Provide information about obtaining API keys"""
    api_info = {
        "EXCHANGE_RATE_API_KEY": "https://www.exchangerate-api.com/docs/free",
        "ALPHA_VANTAGE_API_KEY": "https://www.alphavantage.co/support/#api-key",
    }

    print(f"\n{Color.BOLD}API Key Resources:{Color.END}")
    for var, url in api_info.items():
        if not os.getenv(var) or os.getenv(var, "").endswith("_here"):
            print(f"  {var}: {url}")


def main():
    """Main validation function"""
    print_header("Personal Finance App - Environment Validation")

    # Check if .env file exists
    if not check_env_file():
        sys.exit(1)

    # Load environment variables
    load_dotenv()

    # Validate required variables
    print(f"\n{Color.BOLD}Required Variables:{Color.END}")
    missing, invalid = validate_required_vars()

    # Validate optional variables
    validate_optional_vars()

    # Validate DATABASE_URL format
    print(f"\n{Color.BOLD}Database URL Validation:{Color.END}")
    validate_database_url()

    # Show API key info if needed
    if invalid:
        check_api_keys()

    # Final summary
    print_header("Validation Summary")

    if missing:
        print_error(f"Found {len(missing)} missing required variable(s)")
        print("\nPlease add these variables to your .env file:")
        for var in missing:
            print(f"  - {var}")
        sys.exit(1)
    elif invalid:
        print_warning(f"Found {len(invalid)} variable(s) with placeholder values")
        print("\nPlease update these variables in your .env file:")
        for var in invalid:
            print(f"  - {var}")
        print(
            f"\n{Color.YELLOW}The application may not work correctly until these are configured.{Color.END}"
        )
        sys.exit(1)
    else:
        print_success("All required environment variables are configured!")
        print_success("Your environment is ready to use.")
        sys.exit(0)


if __name__ == "__main__":
    main()
