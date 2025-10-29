import json
from datetime import datetime, timezone
from decimal import Decimal

import requests

from backend.common.base_fetcher import BaseFetcher


class ForexExchangeRateFetcher(BaseFetcher):
    """Utility class to fetch forex rates"""

    def __init__(self):
        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "forex"

        super().__init__("Forex_exchange_rate_fetcher", self.cache_key_prefix, self.cache_expiry_in_seconds)
        self.logger.info("Forex Exchange rate fetcher initialized successfully")

    def get_exchange_rates(self, from_currency: str, to_currency: str):
        """Fetch exchange rate with caching"""
        cache_key = f"{self.cache_key_prefix}"
        currency_pair = f"{from_currency.upper()}-{to_currency.upper()}"

        # --- Try cache first ---
        cached_map = self.get_from_cache(cache_key, [currency_pair])
        cached_info = cached_map.get(currency_pair)

        if cached_info:
            try:
                rate = Decimal(str(cached_info["rate"]))
                self.logger.info(f"Cache hit: {from_currency}->{to_currency} = {rate}")
                return rate
            except (KeyError, ValueError, TypeError) as e:
                self.logger.warning(f"Invalid cached rate for {from_currency}->{to_currency}, refetching: {e}")

        # --- Cache miss: fetch from API ---
        url = f"{self.open_exchange_url}{self.open_exchange_api_key}/pair/{from_currency.upper()}/{to_currency.upper()}"
        self.logger.info(f"Fetching exchange rates from {url}")

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()
            exchange_rate = Decimal(str(data.get("conversion_rate", "1.0")))

            # --- Cache the fetched rate ---
            payload = {
                "from": from_currency.upper(),
                "to": to_currency.upper(),
                "rate": str(exchange_rate),
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "source": "open-exchange"
            }

            try:
                self.set_cache(cache_key, {currency_pair: payload})
                self.logger.info(f"Cached exchange rate {from_currency}->{to_currency}: {exchange_rate}")
            except Exception as e:
                self.logger.warning(f"Cache write failed for {from_currency}->{to_currency}: {e}")

            return exchange_rate

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error fetching exchange rate: {e}")
            return Decimal("1.0")
        except (ValueError, json.JSONDecodeError) as e:
            self.logger.error(f"Error parsing exchange rate response: {e}")
            return Decimal("1.0")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching exchange rate: {e}")
            return Decimal("1.0")


# Global configuration instance
forexFetcher = ForexExchangeRateFetcher()
