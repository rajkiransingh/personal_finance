import hashlib
import json
import os
from datetime import datetime, timezone, UTC
from typing import Dict

import requests
from sqlalchemy.orm import Session

from backend.common.setup import AppConfig, config
from backend.models.investments.crypto import CryptoInvestment, CryptoSummary


class CryptoCurrencyRateFetcher:
    """Utility class to fetch cryptocurrency rates"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Crypto_currency_price_fetcher",
                                             "Crypto_currency_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        self.logger.info("Crypto currency price fetcher initialized successfully")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "cryptocurrency:"
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

    def get_cache_key(self, coin_symbol_list: list) -> str:
        """Generate a consistent cache key based on coin symbols

        Args:
            coin_symbol_list:
        """

        # Sort the list to ensure consistent cache keys regardless of input order
        sorted_symbols = sorted([s.upper() for s in coin_symbol_list])
        symbols_str = ",".join(sorted_symbols)
        # Create a hash to keep cache keys manageable
        hash_obj = hashlib.md5(symbols_str.encode())
        return f"{self.cache_key_prefix}:{hash_obj.hexdigest()}"

    def fetch_cryptocurrency_data_in_usd(self, coin_symbol_list: list, use_cache: bool = True):
        """
        Fetch cryptocurrency data using CoinMarketCap API with Redis caching
    
        Args:
            coin_symbol_list: List of cryptocurrency symbols to fetch
            use_cache: Whether to use Redis cache (default: True)
        """
        cache_key = self.get_cache_key(coin_symbol_list)
        currency_symbol = self.currency.get(3)
        # Try to get data from cache first
        if use_cache:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    self.logger.info(f"Retrieved cryptocurrency data from cache for key: {cache_key}")
                    return json.loads(cached_data)
            except Exception as e:
                self.logger.warning(f"Failed to retrieve data from Redis cache: {e}")
                # Continue with API call if cache fails

        crypto_data = {}

        # Get API key from environment variables
        cmc_api_key = os.environ.get('COIN_MARKET_CAP_API_KEY')

        if not cmc_api_key:
            self.logger.error("CoinMarketCap API key not found in environment variables")
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

            self.logger.info("Fetching cryptocurrency data from CoinMarketCap API")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            all_crypto_data = response.json()

            if 'data' not in all_crypto_data:
                self.logger.error("Invalid response from CoinMarketCap API")
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
                    self.logger.info(f"Added crypto {symbol}: {currency_symbol}{crypto_data[symbol]['price']}")

            # Cache the data in Redis
            if crypto_data and use_cache:
                try:
                    # Add metadata to cached data
                    cached_payload = {
                        'data': crypto_data,
                        'cached_at': datetime.now(timezone.utc).isoformat(),
                        'cache_expiry_seconds': self.cache_expiry_in_seconds
                    }

                    self.redis_client.setex(
                        cache_key,
                        self.cache_expiry_in_seconds,
                        json.dumps(cached_payload)
                    )
                    self.logger.info(
                        f"Cached cryptocurrency data in Redis with key: {cache_key}, expiry: {self.cache_expiry_in_seconds}s")
                except Exception as e:
                    self.logger.warning(f"Failed to cache data in Redis: {e}")
                    # Continue without caching if Redis fails

            self.logger.info(f"Successfully fetched {len(crypto_data)} cryptocurrencies")
            return crypto_data

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch cryptocurrency data: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse cryptocurrency API response: {e}")
            return {"error": f"JSON parsing failed: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Unexpected error fetching cryptocurrency data: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

    def update_crypto_investments(self, db: Session, crypto_data: Dict) -> Dict:
        """
        Update CryptoInvestment table with current prices

        Args:
            db: Database session
            crypto_data: Dictionary with current crypto prices

        Returns:
            Dictionary with update results
        """
        today = datetime.now(UTC)

        currency_map = {
            1: "INR",
            2: "PLN",
            3: "USD"
        }

        try:
            updated_count = 0
            errors = []
            self.logger.info(f"Received updates for cryptocurrency data: {crypto_data}")

            # Get all crypto investments that need updating
            crypto_investments = db.query(CryptoInvestment).filter(
                CryptoInvestment.coin_symbol.in_(list(crypto_data['data'].keys()))
            ).all()

            for investment in crypto_investments:
                currency_symbol = self.currency.get(3)
                try:
                    symbol = investment.coin_symbol.upper()
                    self.logger.info(f"Updating cryptocurrency data for {symbol}")
                    if symbol in crypto_data['data']:
                        current_price = crypto_data['data'][symbol]['price']
                        self.logger.info(f"Current price for {symbol}: {currency_symbol}{current_price}")

                        invested_currency = currency_map.get(investment.currency_id, "INR")
                        # conversion_rate = 1.0

                        if invested_currency == "INR":
                            conversion_rate = round(float(self.redis_forex_key_usd_inr), 2)
                        elif invested_currency == "PLN":
                            conversion_rate = round(float(self.redis_forex_key_usd_pln), 2)
                        elif invested_currency == "USD":
                            conversion_rate = 1.0
                        else:
                            raise Exception(f"Unsupported currency type: {invested_currency}")

                        current_value = (current_price * investment.coin_quantity) * conversion_rate

                        initial_investment = investment.total_invested_amount

                        roi_value = ((current_value - initial_investment) /
                                     investment.total_invested_amount * 100)

                        # Calculate XIRR (simplified version)
                        days_invested = (today.date() - investment.investment_date).days
                        years = days_invested / 365.0

                        # updating the crypto investment table with current values and roi
                        investment.current_price_per_coin = current_price * conversion_rate
                        investment.current_total_value = current_value
                        investment.return_on_investment = roi_value
                        investment.xirr = (((current_value / initial_investment) ** (
                                1 / years)) - 1) * 100 if years > 0 else 0.0

                        updated_count += 1
                        self.logger.info(f"Updated {symbol} investment: {currency_symbol}{current_price}")

                except Exception as e:
                    error_msg = f"Error updating investment {investment.id}: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} crypto investments")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update crypto investments: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }

    def update_crypto_summary(self, db: Session, crypto_data: Dict) -> Dict:

        """
        Update CryptoSummary table with current prices

        Args:
            db: Database session
            crypto_data: Dictionary with current crypto prices

        Returns:
            Dictionary with update results
        """

        try:
            updated_count = 0
            errors = []
            self.logger.info(f"Received updates for cryptocurrency data: {crypto_data}")

            # Get all crypto investments that need updating
            crypto_summaries = db.query(CryptoSummary).all()
            investments = db.query(CryptoInvestment).filter().all()

            currency_symbol = self.currency.get(1)
            for summary in crypto_summaries:
                try:
                    symbol = summary.coin_symbol.upper()
                    self.logger.info(f"Updating cryptocurrency data for {symbol}")
                    conversion_rate = round(float(self.redis_forex_key_usd_inr), 2)

                    if symbol in crypto_data['data']:
                        current_price_inr = crypto_data['data'][symbol]['price'] * conversion_rate
                        self.logger.info(f"Current price for {symbol} in INR: {currency_symbol}{current_price_inr}")

                        current_value = round((current_price_inr * summary.total_quantity), 2)

                        initial_investment = summary.total_cost
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Weighted average XIRR calculation from CryptoInvestment
                        relevant_investments = [
                            inv for inv in investments if inv.coin_symbol == symbol
                        ]

                        if relevant_investments:
                            total_weighted_xirr = sum(
                                (investment.total_invested_amount / initial_investment) * investment.xirr
                                for investment in relevant_investments
                            )
                            self.logger.info(
                                f"Total weighted xirr calculated is: {currency_symbol}{total_weighted_xirr}")
                        else:
                            total_weighted_xirr = 0.0

                        # Update Summary table
                        summary.current_price_per_unit = current_price_inr
                        summary.current_value = current_value
                        summary.roi = roi_value
                        summary.xirr = total_weighted_xirr
                        summary.last_updated = datetime.utcnow()

                        updated_count += 1
                        self.logger.info(
                            f"Updated {symbol} investment with price: {currency_symbol}{current_price_inr}")

                except Exception as e:
                    error_msg = f"Error updating investment {summary.id}: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} crypto investments")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update crypto investments: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }

    def clear_crypto_cache(self, coin_symbol_list: list = None, cache_key_prefix=None):
        """
        Clear cryptocurrency cache for specific coins or all crypto cache

        Args:
            cache_key_prefix:
            coin_symbol_list: Specific coins to clear cache for, or None for all
        """
        try:
            if coin_symbol_list:
                cache_key = self.get_cache_key(coin_symbol_list)
                self.redis_client.delete(cache_key)
                self.logger.info(f"Cleared cache for key: {cache_key}")
            else:
                # Clear all crypto cache keys
                keys = self.redis_client.keys(f"{cache_key_prefix}:*")
                if keys:
                    self.redis_client.delete(*keys)
                    self.logger.info(f"Cleared {len(keys)} cryptocurrency cache keys")
                else:
                    self.logger.info("No cryptocurrency cache keys found to clear")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")

    def get_cache_info(self, coin_symbol_list: list):
        """
        Get information about cached data

        Args:
            coin_symbol_list: List of cryptocurrency symbols to check cache for

        Returns:
            Dict with cache information or None if not cached
        """
        try:
            cache_key = self.get_cache_key(coin_symbol_list)
            ttl = self.redis_client.ttl(cache_key)

            if ttl == -2:  # Key doesn't exist
                return None
            elif ttl == -1:  # Key exists but no expiry set
                return {"status": "cached", "ttl": "no_expiry", "cache_key": cache_key}
            else:
                return {"status": "cached", "ttl_seconds": ttl, "cache_key": cache_key}
        except Exception as e:
            self.logger.error(f"Failed to get cache info: {e}")
            return None


# Global configuration instance
CryptoFetcher = CryptoCurrencyRateFetcher()
