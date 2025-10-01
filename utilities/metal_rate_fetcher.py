import json
import os
from datetime import datetime, timezone, UTC
from typing import Dict

import requests
from sqlalchemy.orm import Session

from backend.common.setup import AppConfig, config
from backend.models.investments.bullion import BullionInvestment, BullionSummary


class MetalRateFetcher:
    """Utility class to fetch bullion rates"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Bullion_price_fetcher",
                                             "Bullion_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        self.logger.info("Bullion price fetcher initialized successfully")

        # Load config data from environment
        self.rapid_api_host = os.getenv("RAPID_API_HOST")
        self.base_url = os.getenv("RAPID_API_BASE_URL")
        self.gold_url = os.getenv("GOLD_API")
        self.silver_url = os.getenv("SILVER_API")
        self.rapid_api_key = os.getenv("RAPID_API_KEY")
        self.cache_expiry_in_seconds = 86400 * 15  # 9 Days
        self.cache_key_prefix = "bullion:"

    DEFAULT_CITY = os.getenv("CITY")
    DEFAULT_PURITY = "24k"

    def get_gold_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        return self.get_current_metal_rates('gold', city, purity)

    def get_silver_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        # self.redis_client.delete(f"{self.cache_key_prefix}:{purity}:{city.lower()}")
        return self.get_current_metal_rates('silver', city, purity)

    def get_current_metal_rates(self, metal: str, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        cache_key = f"{self.cache_key_prefix}:{metal}:{city.lower()}"

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
        if not self.rapid_api_key:
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
            'x-rapidapi-key': self.rapid_api_key
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

    def update_bullion_investments(self, db: Session, bullion_data: Dict) -> Dict:

        today = datetime.now(UTC)
        updated_count = 0
        errors = []
        try:
            for metal, current_price in bullion_data.items():
                # Get all bullion investments that need updating
                bullion_investments = (
                    db.query(BullionInvestment)
                    .filter(BullionInvestment.metal_name == metal)
                    .all()
                )

                currency_symbol = "₹"
                for investment in bullion_investments:
                    try:
                        self.logger.info(f"Updating Bullion investment data for {metal}")
                        self.logger.info(f"Current price for {metal} in INR: {currency_symbol}{current_price}")

                        current_value = current_price * investment.quantity_in_grams
                        initial_investment = investment.total_invested_amount

                        # Update current price and calculated fields
                        investment.current_price_per_gram = current_price
                        investment.current_total_value = current_value

                        roi_value = ((investment.current_total_value - initial_investment) /
                                     initial_investment * 100)
                        # Calculate return on investment
                        investment.return_on_investment = roi_value

                        # Calculate XIRR (simplified version)
                        days_invested = (today.date() - investment.investment_date).days
                        years = days_invested / 365.0

                        investment.xirr = (((current_value / initial_investment) ** (
                                1 / years)) - 1) * 100 if years > 0 else 0.0

                        updated_count += 1
                        self.logger.debug(f"Updated {metal} investment: ${current_price}")

                    except Exception as e:
                        self.logger.error(f"Failed to update {metal} investment: {e}")

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} bullion investments")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update bullion investments: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }

    def update_bullion_summary(self, db: Session, bullion_data: Dict) -> Dict:
        updated_count = 0
        errors = []

        try:
            for metal, current_price in bullion_data.items():
                self.logger.info(f"Received updates for bullion data: {bullion_data}")

                # Get all crypto investments that need updating
                bullion_summaries = db.query(BullionSummary).filter(BullionSummary.metal_name == metal).all()
                investments = db.query(BullionInvestment).filter(BullionInvestment.metal_name == metal).all()

                currency_symbol = "₹"
                for summary in bullion_summaries:
                    try:
                        self.logger.info(f"Updating Bullion Summary data for {metal}")
                        self.logger.info(f"Current price for {metal} in INR: {currency_symbol}{current_price}")

                        current_value = round((current_price * summary.total_quantity), 2)

                        initial_investment = summary.total_cost
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Weighted average XIRR calculation from Bullion Investment
                        relevant_investments = [
                            inv for inv in investments if inv.metal_name == metal
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
                        summary.current_price_per_unit = current_price
                        summary.current_value = current_value
                        summary.roi = roi_value
                        summary.xirr = total_weighted_xirr
                        summary.last_updated = datetime.now(UTC)

                        updated_count += 1
                        self.logger.info(
                            f"Updated {metal} investment summary with price: {currency_symbol}{current_price}")

                    except Exception as e:
                        error_msg = f"Error updating investment summary {summary.id}: {e}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} bullion investment summary")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update bullion investment summary: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }


# Global configuration instance
bullionFetcher = MetalRateFetcher()
