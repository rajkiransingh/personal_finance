import os
from decimal import Decimal

import requests

from backend.common.config import AppConfig, config, get_redis_client


class ForexExchangeRateFetcher:
    """Utility class to fetch forex rates"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Forex_exchange_rate_fetcher",
                                             "Forex_exchange_rate_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = get_redis_client()

        self.logger.info("Forex Exchange rate fetcher initialized successfully")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "forex:"
        self.open_exchange_url = os.getenv("EXCHANGE_API_URL")
        self.open_exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    # Set up logging
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.FileHandler("../logs/Exchange_rate_fetcher_logs.log"),
    #         logging.StreamHandler(sys.stdout)
    #     ]
    # )
    # logger = logging.getLogger("get_exchange_rates")

    def get_exchange_rates_old(self, api_key, from_currency, to_currency):
        try:
            url = f'{self.open_exchange_url}{api_key}/pair/{from_currency}/{to_currency}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                return Decimal(data['conversion_rate', 1.0])
            else:
                self.logger.error(f"Error fetching exchange rates. Status Code: {response.status_code}")
                return 1.0

        except Exception as e:
            self.logger.error(f"Error fetching exchange rates: {e}")
            return 1.0

    def get_exchange_rates(self, from_currency, to_currency):
        """Fetch exchange rate with caching"""
        cache_key = f"{self.cache_key_prefix}:{from_currency}:{to_currency}"

        # Check Redis cache
        cached_rate = self.redis_client.get(cache_key)
        if cached_rate:
            self.logger.info(f"Cache hit: Using cached exchange rate for {from_currency} to {to_currency}")
            return Decimal(cached_rate)

        url = f"{self.open_exchange_url}{self.open_exchange_api_key}/pair/{from_currency}/{to_currency}"

        try:
            self.logger.info(f"Fetching exchange rate for {from_currency} to {to_currency}")
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                exchange_rate = Decimal(data.get('conversion_rate', 1.0))

                # Store in Redis with a 24-hour expiry
                self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, str(exchange_rate))

                return exchange_rate
            else:
                self.logger.error(f"Cache miss: Error fetching exchange rates. Status Code: {response.status_code}")
                return Decimal(1.0)

        except Exception as e:
            self.logger.error(f"Error fetching exchange rates: {e}")
            return Decimal(1.0)
