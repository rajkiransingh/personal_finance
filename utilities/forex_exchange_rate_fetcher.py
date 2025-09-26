import os
from decimal import Decimal

import requests

from backend.common.setup import AppConfig, config


class ForexExchangeRateFetcher:
    """Utility class to fetch forex rates"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Forex_exchange_rate_fetcher",
                                             "Forex_exchange_rate_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        self.logger.info("Forex Exchange rate fetcher initialized successfully")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "forex:"
        self.open_exchange_url = os.getenv("EXCHANGE_API_URL")
        self.open_exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    def get_exchange_rates(self, from_currency: str, to_currency: str):
        """Fetch exchange rate with caching"""
        cache_key = f"{self.cache_key_prefix}:{from_currency.upper()}:{to_currency.upper()}"

        # Check Redis cache
        cached_rate = self.redis_client.get(cache_key)
        if cached_rate:
            self.logger.info(
                f"Cache hit: Using cached exchange rate for {from_currency} to {to_currency}: {cached_rate}")
            return Decimal(cached_rate)

        url = f"{self.open_exchange_url}{self.open_exchange_api_key}/pair/{from_currency.upper()}/{to_currency.upper()}"

        self.logger.info(f"Fetching exchange rates from {url}")
        try:
            self.logger.info(f"Fetching exchange rate for {from_currency} to {to_currency}")
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                exchange_rate = Decimal(data.get('conversion_rate', 1.0))

                # Store in Redis with a 24-hour expiry
                self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, str(exchange_rate))
                self.logger.info(f"Fetched rate is for {from_currency} to {to_currency} is {exchange_rate}")
                return exchange_rate
            else:
                self.logger.error(f"Cache miss: Error fetching exchange rates. Status Code: {response.status_code}")
                return Decimal(1.0)

        except Exception as e:
            self.logger.error(f"Error fetching exchange rates: {e}")
            return Decimal(1.0)


# Global configuration instance
forexFetcher = ForexExchangeRateFetcher()
