import json
from datetime import datetime, timezone

import requests
import redis
import os
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Bullion_rate_fetcher_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("get_current_metal_rates")

# Redis Config
logger.info("Setup Redis Client...")
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Some config data
rapid_api_host = os.getenv("RAPID_API_HOST")
base_url = os.getenv("RAPID_API_BASE_URL")
gold_url = os.getenv("GOLD_API")
silver_url = os.getenv("SILVER_API")
rapidapi_key = os.getenv('RAPID_API_KEY')
DEFAULT_CITY = os.getenv("CITY")
DEFAULT_PURITY = "24k"
CACHE_EXPIRY_SECONDS = 259200 * 3 # 9 Days

def get_gold_rate(city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
    return get_current_metal_rates('gold', city, purity)

def get_silver_rate(city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
    return get_current_metal_rates('silver', city, purity)

def get_current_metal_rates(metal: str, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
    cache_key = f"{metal.lower()}_rate:{purity}:{city.lower()}"

    # Check Redis cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        try:
            cached_info = json.loads(cached_data)
            rate = float(cached_info['rate'])  # Convert to float first
            logger.info(f"Cache hit: Using cached {metal} rate for {city}: {rate}")
            return int(rate)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cached data for {metal} in {city}, will refetch: {e}")
    else:
        logger.info(f"Cache miss: No cached {metal} rate for {city}")

    # Get API credentials
    if not rapidapi_key:
        logger.error("RAPID_API_KEY not found in environment variables")
        raise ValueError("RAPID_API_KEY not configured")

    # Configure API endpoint based on metal type
    if metal.lower() == 'gold':
        endpoint = f"{base_url}{gold_url}"
    else:
        endpoint = f"{base_url}{silver_url}"

    headers = {
        'city': city,
        'x-rapidapi-host': rapid_api_host,
        'x-rapidapi-key': rapidapi_key
    }

    try:
        logger.info(f"Fetching {metal} rate from RapidAPI for city: {city}")
        response = requests.get(endpoint, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Fetched {metal} data: {data}")

        rate = extract_rate_from_response(data, metal, city)

        if rate is None:
            logger.error(f"Could not extract {metal} rate for purity {purity}")
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
            redis_client.setex(cache_key, CACHE_EXPIRY_SECONDS, json.dumps(cache_data))
            logger.info(f"Cached {metal} rate in Redis for {city}: {rate}")
        except Exception as e:
            logger.warning(f"Failed to cache {metal} rate: {e}")

        return int(rate)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {metal} rate from RapidAPI: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {metal} API response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {metal} rate: {e}")
        return None

def extract_rate_from_response(data: dict, metal: str, city: str):
    try:
        # Check if API returned an error
        if data.get('Status_code') != 200:
            logger.error(f"API returned error status: {data.get('Status_code')}")
            return None

        # Look for the city-specific rate key: "CityName_1g"
        if metal.lower() == 'gold':
            city_key = f"{city}_{DEFAULT_PURITY}"
        else:
            city_key = f"{city}_1g"

        if city_key in data:
            rate = data[city_key]
            return float(rate)  # Convert to float before returning

        # Log the full response for debugging
        logger.debug(f"Full API response: {data}")
        return None

    except Exception as e:
        logger.error(f"Error extracting metal rate from response: {e}")
        return None