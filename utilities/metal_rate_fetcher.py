import json
import os
from datetime import datetime, timezone

import requests

from backend.common.config import AppConfig, config, get_redis_client


class MetalRateFetcher:
    """Utility class to fetch bullion rates"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Bullion_price_fetcher",
                                             "Bullion_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = get_redis_client()

        self.logger.info("Bullion price fetcher initialized successfully")

        # Load config data from environment
        self.rapid_api_host = os.getenv("RAPID_API_HOST")
        self.base_url = os.getenv("RAPID_API_BASE_URL")
        self.gold_url = os.getenv("GOLD_API")
        self.silver_url = os.getenv("SILVER_API")
        self.rapidapi_key = os.getenv("RAPID_API_KEY")
        self.cache_expiry_in_seconds = 86400 * 9  # 9 Days
        self.cache_key_prefix = "bullion:"

    # # Set up logging
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.FileHandler("./logs/Bullion_rate_fetcher_logs.log"),
    #         logging.StreamHandler(sys.stdout)
    #     ]
    # )
    # logger = logging.getLogger("get_current_metal_rates")
    #
    # # Redis Config
    # logger.info("Setup Redis Client...")
    # REDIS_HOST = "redis"
    # REDIS_PORT = 6379
    # redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    DEFAULT_CITY = os.getenv("CITY")
    DEFAULT_PURITY = "24k"

    def get_gold_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        return self.get_current_metal_rates('gold', city, purity)

    def get_silver_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        return self.get_current_metal_rates('silver', city, purity)

    def get_current_metal_rates(self, metal: str, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        cache_key = f"{self.cache_key_prefix}:{purity}:{city.lower()}"

        # Check Redis cache first
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            try:
                cached_info = json.loads(cached_data)
                rate = float(cached_info['rate'])  # Convert to float first
                self.logger.info(f"Cache hit: Using cached {metal} rate for {city}: {rate}")
                return int(rate)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.logger.warning(f"Invalid cached data for {metal} in {city}, will refetch: {e}")
        else:
            self.logger.info(f"Cache miss: No cached {metal} rate for {city}")

        # Get API credentials
        if not self.rapidapi_key:
            self.logger.error("RAPID_API_KEY not found in environment variables")
            raise ValueError("RAPID_API_KEY not configured")

        # Configure API endpoint based on metal type
        if metal.lower() == 'gold':
            endpoint = f"{self.base_url}{self.gold_url}"
        else:
            endpoint = f"{self.base_url}{self.silver_url}"

        headers = {
            'city': city,
            'x-rapidapi-host': self.rapid_api_host,
            'x-rapidapi-key': self.rapidapi_key
        }

        try:
            self.logger.info(f"Fetching {metal} rate from RapidAPI for city: {city}")
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.logger.info(f"Fetched {metal} data: {data}")

            rate = self.extract_rate_from_response(data, metal, city)

            if rate is None:
                self.logger.error(f"Could not extract {metal} rate for purity {purity}")
                return None

            # Cache the result
            cache_data = {
                'rate': rate,
                'metal': metal,
                'city': city,
                'purity': purity,
                'cached_at': datetime.now(timezone.utc).isoformat(),
                'source': 'rapidapi'
            }

            try:
                self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(cache_data))
                self.logger.info(f"Cached {metal} rate in Redis for {city}: {rate}")
            except Exception as e:
                self.logger.warning(f"Failed to cache {metal} rate: {e}")

            return int(rate)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch {metal} rate from RapidAPI: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse {metal} API response: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {metal} rate: {e}")
            return None

    def extract_rate_from_response(self, data: dict, metal: str, city: str, purity: str = DEFAULT_PURITY):
        try:
            # Check if API returned an error
            if data.get('Status_code') != 200:
                self.logger.error(f"API returned error status: {data.get('Status_code')}")
                return None

            # Look for the city-specific rate key: "CityName_1g"
            if metal.lower() == 'gold':
                city_key = f"{city}_{purity}"
            else:
                city_key = f"{city}_1g"

            if city_key in data:
                rate = data[city_key]
                return float(rate)  # Convert to float before returning

            # Log the full response for debugging
            self.logger.debug(f"Full API response: {data}")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting metal rate from response: {e}")
            return None
