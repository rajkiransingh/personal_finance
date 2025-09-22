import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone

import redis
import requests

# Create logs directory if it doesn't exist
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Crypto_fetcher_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("get_crypto_rates")

# Redis Config
logger.info("Initialize Redis Client")
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Cache configuration
CACHE_EXPIRY_SECONDS = 86400  # 1 day cache expiry
CACHE_KEY_PREFIX = "crypto_data"

def get_cache_key(coin_symbol_list: list) -> str:
    """Generate a consistent cache key based on coin symbols"""
    # Sort the list to ensure consistent cache keys regardless of input order
    sorted_symbols = sorted([s.upper() for s in coin_symbol_list])
    symbols_str = ",".join(sorted_symbols)
    # Create a hash to keep cache keys manageable
    hash_obj = hashlib.md5(symbols_str.encode())
    return f"{CACHE_KEY_PREFIX}:{hash_obj.hexdigest()}"

def fetch_cryptocurrency_data(coin_symbol_list: list, use_cache: bool = True):
    """
    Fetch cryptocurrency data using CoinMarketCap API with Redis caching

    Args:
        coin_symbol_list: List of cryptocurrency symbols to fetch
        use_cache: Whether to use Redis cache (default: True)
    """
    cache_key = get_cache_key(coin_symbol_list)

    # Try to get data from cache first
    if use_cache:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Retrieved cryptocurrency data from cache for key: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to retrieve data from Redis cache: {e}")
            # Continue with API call if cache fails

    crypto_data = {}

    # Get API key from environment variables
    cmc_api_key = os.environ.get('COIN_MARKET_CAP_API_KEY')

    if not cmc_api_key:
        logger.error("CoinMarketCap API key not found in environment variables")
        return {"error": "API key not configured"}

    try:
        # CoinMarketCap API call
        url = os.getenv('COIN_MARKET_URL')
        headers = {
            'X-CMC_PRO_API_KEY': cmc_api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'deflate, gzip'
        }
        params = {
            'limit': 100,  # Get top 100 coins
            'convert': 'USD'
        }

        logger.info("Fetching cryptocurrency data from CoinMarketCap API")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        all_crypto_data = response.json()

        if 'data' not in all_crypto_data:
            logger.error("Invalid response from CoinMarketCap API")
            return {"error": "Invalid API response"}

        # Filter for your portfolio coins
        for coin in all_crypto_data['data']:
            symbol = coin.get('symbol', '').upper()

            if symbol in [s.upper() for s in coin_symbol_list]:
                quote_data = coin.get('quote', {}).get('USD', {})

                crypto_data[symbol] = {
                    'name': coin.get('name'),
                    'symbol': symbol,
                    'price': round(float(quote_data.get('price', 0)), 8),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                logger.info(f"Added crypto {symbol}: ${crypto_data[symbol]['price']}")

        # Cache the data in Redis
        if crypto_data and use_cache:
            try:
                # Add metadata to cached data
                cached_payload = {
                    'data': crypto_data,
                    'cached_at': datetime.now(timezone.utc).isoformat(),
                    'cache_expiry_seconds': CACHE_EXPIRY_SECONDS
                }

                redis_client.setex(
                    cache_key,
                    CACHE_EXPIRY_SECONDS,
                    json.dumps(cached_payload)
                )
                logger.info(
                    f"Cached cryptocurrency data in Redis with key: {cache_key}, expiry: {CACHE_EXPIRY_SECONDS}s")
            except Exception as e:
                logger.warning(f"Failed to cache data in Redis: {e}")
                # Continue without caching if Redis fails

        logger.info(f"Successfully fetched {len(crypto_data)} cryptocurrencies")
        return crypto_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch cryptocurrency data: {e}")
        return {"error": f"API request failed: {str(e)}"}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse cryptocurrency API response: {e}")
        return {"error": f"JSON parsing failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error fetching cryptocurrency data: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def clear_crypto_cache(coin_symbol_list: list = None):
    """
    Clear cryptocurrency cache for specific coins or all crypto cache

    Args:
        coin_symbol_list: Specific coins to clear cache for, or None for all
    """
    try:
        if coin_symbol_list:
            cache_key = get_cache_key(coin_symbol_list)
            redis_client.delete(cache_key)
            logger.info(f"Cleared cache for key: {cache_key}")
        else:
            # Clear all crypto cache keys
            keys = redis_client.keys(f"{CACHE_KEY_PREFIX}:*")
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cryptocurrency cache keys")
            else:
                logger.info("No cryptocurrency cache keys found to clear")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")


def get_cache_info(coin_symbol_list: list):
    """
    Get information about cached data

    Args:
        coin_symbol_list: List of cryptocurrency symbols to check cache for

    Returns:
        Dict with cache information or None if not cached
    """
    try:
        cache_key = get_cache_key(coin_symbol_list)
        ttl = redis_client.ttl(cache_key)

        if ttl == -2:  # Key doesn't exist
            return None
        elif ttl == -1:  # Key exists but no expiry set
            return {"status": "cached", "ttl": "no_expiry", "cache_key": cache_key}
        else:
            return {"status": "cached", "ttl_seconds": ttl, "cache_key": cache_key}
    except Exception as e:
        logger.error(f"Failed to get cache info: {e}")
        return None