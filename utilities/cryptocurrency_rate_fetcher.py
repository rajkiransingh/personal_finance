import json
import os
from datetime import datetime, timezone, UTC
from typing import Dict

import requests
from sqlalchemy.orm import Session

from backend.common.base_fetcher import BaseFetcher
from backend.models.investments.crypto import CryptoInvestment, CryptoSummary


class CryptoCurrencyRateFetcher(BaseFetcher):
    """Utility class to fetch cryptocurrency rates"""

    def __init__(self):
        self.cache_key_prefix = "cryptocurrency"
        super().__init__("Crypto_currency_price_fetcher", self.cache_key_prefix, cache_expiry_seconds=86400)

        self.logger.info("Crypto currency price fetcher initialized successfully")

    def fetch_coin_data(self, symbols: list):
        cached_map = self.get_from_cache(self.cache_key_prefix, symbols)
        missing_symbols = [sym for sym, val in cached_map.items() if val is None]
        fetched = {}
        errors = {}

        if not missing_symbols:
            self.logger.info("Cache hit for all symbols — using cached data only")
            return {"data": cached_map, "errors": {}}

        url = os.getenv('COIN_MARKET_URL')
        api_key = os.getenv('COIN_MARKET_CAP_API_KEY')
        headers = {'X-CMC_PRO_API_KEY': api_key, 'Accept': 'application/json'}

        try:
            for symbol in missing_symbols:
                try:
                    self.logger.info(f"Fetching {symbol} from CoinMarketCap API")
                    resp = requests.get(url, headers=headers, params={'symbol': symbol, 'convert': 'USD'}, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()

                    if 'data' not in data or symbol not in data['data']:
                        msg = "no_data_in_api_response"
                        self.logger.warning(f"API returned no data for {symbol}")
                        errors[symbol] = msg
                        fetched[symbol] = None
                        continue

                    fetched[symbol] = data['data'][symbol]

                except requests.exceptions.Timeout:
                    self.logger.error(f"Timeout when fetching {symbol}")
                    errors[symbol] = "timeout"
                    fetched[symbol] = None
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Request error for {symbol}: {e}")
                    errors[symbol] = f"request_error: {str(e)}"
                    fetched[symbol] = None
                except (ValueError, json.JSONDecodeError) as e:
                    self.logger.error(f"Parsing error for {symbol}: {e}")
                    errors[symbol] = f"parsing_error: {str(e)}"
                    fetched[symbol] = None
                except Exception as e:
                    self.logger.error(f"Unexpected error for {symbol}: {e}")
                    errors[symbol] = f"unexpected_error: {str(e)}"
                    fetched[symbol] = None

            # Cache only successful fetches (non-None)
            to_cache = {s: v for s, v in fetched.items() if v is not None}
            if to_cache:
                try:
                    self.logger.info(f"Caching {len(to_cache)} new items: {list(to_cache.keys())}")
                    self.set_cache(self.cache_key_prefix, to_cache)
                except Exception as e:
                    self.logger.warning(f"Failed to write fetched items to cache: {e}")

        except Exception as e:
            self.logger.error(f"Unexpected outer error while fetching missing symbols: {e}")
            for sym in missing_symbols:
                errors.setdefault(sym, f"unexpected_error: {str(e)}")
                fetched.setdefault(sym, None)

        final_map = {}
        for sym in symbols:
            cached_val = cached_map.get(sym)
            final_map[sym] = cached_val if cached_val is not None else fetched.get(sym)

        return {"data": final_map, "errors": errors}

    def fetch_cryptocurrency_data_in_usd(self, coin_symbol_list: list, use_cache: bool = True):
        """
        Fetch cryptocurrency data using CoinMarketCap API with Redis caching

        Args:
            coin_symbol_list: List of cryptocurrency symbols to fetch
            use_cache: Whether to use Redis cache (default: True)
        """
        currency_symbol = self.currency.get(3)
        response = self.fetch_coin_data(coin_symbol_list)

        if "error" in response and response["error"]:
            self.logger.error(f"Failed to fetch cryptocurrency data: {response['error']}")
            return {"error": response["error"]}

        all_crypto_data = response
        if "data" not in all_crypto_data:
            self.logger.error("Invalid response from CoinMarketCap API")
            return {"error": "Invalid API response"}

        crypto_data = {}
        for coin in coin_symbol_list:
            coin_data = all_crypto_data["data"].get(coin)
            if not coin_data:
                self.logger.warning(f"No data found for {coin}, skipping...")
                continue

            symbol = coin_data.get("symbol", "").upper()
            quote_data = coin_data.get("quote", {}).get("USD", {})

            crypto_data[symbol] = {
                "name": coin_data.get("name"),
                "symbol": symbol,
                "price": round(float(quote_data.get("price", 0)), 8),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            self.logger.info(f"Fetched {symbol}: {currency_symbol}{crypto_data[symbol]['price']}")

        self.logger.info(f"Successfully fetched {len(crypto_data)} cryptocurrencies")
        return {"data": crypto_data}

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

                        invested_currency = self.currency_map.get(investment.currency_id, "INR")
                        conversion_rate = self.get_conversion_rate_from_usd(invested_currency)

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

                        if years >= 1:
                            investment.xirr = (((current_value / initial_investment) ** (1 / years)) - 1) * 100
                        else:
                            investment.xirr = ((current_value - initial_investment) / initial_investment) * 100

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

            # Get all crypto investments that need updating
            crypto_summaries = db.query(CryptoSummary).all()
            investments = db.query(CryptoInvestment).filter().all()

            currency_symbol = self.currency.get(1)
            for summary in crypto_summaries:
                try:
                    symbol = summary.coin_symbol.upper()
                    self.logger.info(f"Updating cryptocurrency summary data for {symbol}")
                    conversion_rate = round(float(json.loads(self.redis_forex_key_usd_inr)['rate']), 2)

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
                                f"Total weighted xirr calculated is: {round(total_weighted_xirr, 2)}%")
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
                            f"Updated {symbol} investment summary with price: {currency_symbol}{current_price_inr}")

                except Exception as e:
                    error_msg = f"Error updating investment summary {summary.id}: {e}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} crypto investment summary")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update crypto investment summary: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }


# Global configuration instance
CryptoFetcher = CryptoCurrencyRateFetcher()
