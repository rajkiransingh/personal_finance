import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List

from backend.common.setup import config


def _build_cache_key(prefix: str, symbol: str) -> str:
    """Helper: create a standardized cache key"""
    return f"{prefix}::{symbol.upper()}"


class BaseFetcher:
    """Base utility for all data fetchers (Crypto, Bullion, Forex, etc.)"""

    def __init__(self, name: str, cache_prefix: str, cache_expiry_seconds: int = 86400):
        self.logger = config.setup_logger(name)
        self.redis_client = config.redis_client()
        self.cache_prefix = cache_prefix
        self.cache_expiry = cache_expiry_seconds

        # Load config data from environment
        self.rapid_api_bullion_host = os.getenv("RAPID_API_BULLION_HOST")
        self.rapid_api_mf_host = os.getenv("RAPID_API_MF_HOST")
        self.bullion_base_url = os.getenv("RAPID_API_BULLION_BASE_URL")
        self.gold_url = os.getenv("GOLD_API")
        self.silver_url = os.getenv("SILVER_API")
        self.mf_base_url = os.getenv("RAPID_API_MF_BASE_URL")
        self.rapid_api_key = os.getenv("RAPID_MF_API_KEY")
        self.open_exchange_url = os.getenv("EXCHANGE_API_URL")
        self.open_exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY")

        # Getting data from Redis
        self.redis_forex_key_usd_inr = self.redis_client.get("forex::USD:INR")
        self.redis_forex_key_usd_pln = self.redis_client.get("forex::USD:PLN")
        self.redis_forex_key_pln_inr = self.redis_client.get("forex::PLN:INR")

        self.currency = {
            1: "₹",  # INR
            2: "zł",  # PLN
            3: "$",  # USD
        }

        self.currency_map = {
            1: "INR",
            2: "PLN",
            3: "USD"
        }

    def get_conversion_rate(self, currency_code: str) -> float:
        try:
            if currency_code == "INR":
                return round(float(self.redis_forex_key_usd_inr), 2)
            elif currency_code == "PLN":
                return round(float(self.redis_forex_key_usd_pln), 2)
            elif currency_code == "USD":
                return 1.0
            else:
                raise ValueError(f"Unsupported currency type: {currency_code}")
        except (TypeError, ValueError):
            self.logger.warning(f"Missing forex rate for {currency_code}, defaulting to 1.0")
            return 1.0

    def set_cache(self, prefix: str, data: Dict[str, dict], expiry: Optional[int] = None):
        """
        Cache cryptocurrency or asset data individually by symbol.

        Args:
            prefix: cache prefix (e.g., 'cryptocurrency', 'bullion', 'Stock')
            data: dict of {symbol: {price, name, ...}}
            expiry: optional expiry seconds
        """
        try:
            for symbol, value in data.items():
                cache_key = _build_cache_key(prefix, symbol)
                payload = {
                    **value,
                    "cached_at": datetime.now(timezone.utc).isoformat()
                }
                self.redis_client.setex(cache_key, expiry or self.cache_expiry, json.dumps(payload))
                self.logger.info(
                    f"✅ Cached data for {symbol} under key [{cache_key}] (expiry: {expiry or self.cache_expiry}s)")
        except Exception as e:
            self.logger.warning(f"⚠️ Cache write failed for prefix={prefix}: {e}")

    def get_from_cache(self, prefix: str, symbols: List[str]) -> Dict[str, Optional[dict]]:
        """
        Retrieve cached data for multiple symbols.

        Args:
            prefix: cache prefix (e.g., 'cryptocurrency', 'bullion')
            symbols: list of symbols to retrieve

        Returns:
            Dict with symbol as key and cached data as value (None if not cached)
        """
        results = {}
        for symbol in symbols:
            try:
                cache_key = _build_cache_key(prefix, symbol)
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    results[symbol] = json.loads(cached_data)
                    self.logger.info(f"Cache Hit:: Retrieved {symbol} from {cache_key}")
                else:
                    results[symbol] = None
            except Exception as e:
                self.logger.warning(f"Cache read failed for {symbol}: {e}")
                results[symbol] = None
        return results

    def get_cache_info(self, prefix: str, symbols: List[str]) -> Dict[str, dict]:
        """
        Get TTL info for each symbol cache key.

        Args:
            prefix: cache prefix
            symbols: list of symbols to check

        Returns:
            Dict of {symbol: {status, ttl_seconds, cache_key}}
        """
        info = {}
        for symbol in symbols:
            try:
                cache_key = _build_cache_key(prefix, symbol)
                ttl = self.redis_client.ttl(cache_key)
                if ttl == -2:
                    info[symbol] = {"status": "not_cached", "cache_key": cache_key}
                elif ttl == -1:
                    info[symbol] = {"status": "cached", "ttl": "no_expiry", "cache_key": cache_key}
                else:
                    info[symbol] = {"status": "cached", "ttl_seconds": ttl, "cache_key": cache_key}
            except Exception as e:
                self.logger.error(f"Failed to get cache info for {symbol}: {e}")
                info[symbol] = {"status": "error", "cache_key": None, "error": str(e)}
        return info

    def clear_cache(self, prefix: str, symbols: Optional[List[str]] = None):
        """
        Clear cache for specific symbols or entire prefix group.

        Args:
            prefix: cache prefix (e.g., 'cryptocurrency', 'Stock')
            symbols: optional list of symbols to clear. If None, clears all with that prefix.
        """
        try:
            if symbols:
                for symbol in symbols:
                    cache_key = _build_cache_key(prefix, symbol)
                    self.redis_client.delete(cache_key)
                    self.logger.info(f"🧹 Cleared cache for {cache_key}")
            else:
                pattern = f"{prefix}::*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    self.logger.info(f"🧹 Cleared all {len(keys)} cache keys for prefix {prefix}")
                else:
                    self.logger.info(f"No cache keys found for prefix {prefix}")
        except Exception as e:
            self.logger.error(f"Failed to clear cache for prefix {prefix}: {e}")
