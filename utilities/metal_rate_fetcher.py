import json
import os
from datetime import datetime, timezone, UTC
from typing import Dict

import requests
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionInvestment, BullionSummary
from utilities.common.base_fetcher import BaseFetcher
from utilities.common.financial_utils import FinancialCalculator


class MetalRateFetcher(BaseFetcher):
    """Utility class to fetch bullion rates"""

    def __init__(self):
        """Initialize metal rate fetcher with cache configuration.

        Sets up the fetcher with a 9-day cache expiry for bullion rates
        and initializes the base fetcher with bullion-specific configuration.
        """
        # Load config data from environment

        self.cache_expiry_in_seconds = 86400 * 9  # 9 Days
        self.cache_key_prefix = "bullion"

        super().__init__(
            "utilities.metal_fetcher",
            self.cache_key_prefix,
            self.cache_expiry_in_seconds,
        )
        self.logger.debug("Bullion fetcher initialized")

    DEFAULT_CITY = os.getenv("CITY")
    DEFAULT_PURITY = "24k"

    def get_gold_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        """Fetch current gold rate for specified city and purity.

        Args:
            city: City name for which to fetch gold rate (default from env)
            purity: Gold purity level (default: '24k')

        Returns:
            Current gold rate per gram as integer, or None if fetch fails
        """
        return self.get_current_metal_rates("gold", city, purity)

    def get_silver_rate(self, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY):
        """Fetch current silver rate for specified city and purity.

        Args:
            city: City name for which to fetch silver rate (default from env)
            purity: Silver purity level (default: '24k')

        Returns:
            Current silver rate per gram as integer, or None if fetch fails
        """
        # self.redis_client.delete(f"{self.cache_key_prefix}:{purity}:{city.lower()}")
        return self.get_current_metal_rates("silver", city, purity)

    def get_current_metal_rates(
            self, metal: str, city: str = DEFAULT_CITY, purity: str = DEFAULT_PURITY
    ):
        """Fetch current metal rates with caching.

        Attempts to retrieve rate from cache first. On cache miss, fetches from
        RapidAPI and caches the result for future use.

        Args:
            metal: Metal type ('gold' or 'silver')
            city: City name for which to fetch rate (default from env)
            purity: Metal purity level (default: '24k')

        Returns:
            Current metal rate per gram as integer, or None if fetch fails

        Raises:
            ValueError: If RAPID_API_KEY is not configured
        """
        cache_key = f"{self.cache_key_prefix}:{city.lower()}"
        metal = metal.lower()

        # Check Redis cache first
        cached_results = self.get_from_cache(cache_key, [metal])
        cached_info = cached_results.get(metal)

        if cached_info:
            try:
                rate = float(cached_info["rate"])
                self.logger.info(
                    f"Cache hit: Using cached {metal} rate for {city}: {rate}"
                )
                return rate
            except (KeyError, ValueError, TypeError) as e:
                self.logger.warning(
                    f"Invalid cached data for {metal} {city}, refetching: {e}"
                )

        # --- Cache Miss: Fetch Fresh ---
        if not self.rapid_api_key:
            self.logger.error("RAPID_API_KEY not found in environment variables")
            raise ValueError("RAPID_API_KEY not configured")

        endpoint = f"{self.bullion_base_url}{self.gold_url if metal.lower() == 'gold' else self.silver_url}"

        headers = {
            "city": city,
            "x-rapidapi-host": self.rapid_api_bullion_host,
            "x-rapidapi-key": self.rapid_api_key,
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
                "rate": rate,
                "metal": metal,
                "city": city,
                "purity": purity,
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "source": "rapidapi",
            }

            try:
                self.set_cache(
                    cache_key, {metal: cache_data}, expiry=self.cache_expiry_in_seconds
                )
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

    def extract_rate_from_response(
            self, data: dict, metal: str, city: str, purity: str = DEFAULT_PURITY
    ):
        """Extract rate from API response data.

        Parses the API response to extract the metal rate for the specified
        city and purity level.

        Args:
            data: API response data dictionary
            metal: Metal type ('gold' or 'silver')
            city: City name
            purity: Metal purity level (default: '24k')

        Returns:
            Extracted rate as float, or None if extraction fails
        """
        try:
            # Check if API returned an error
            if data.get("Status_code") != 200:
                self.logger.error(
                    f"API returned error status: {data.get('Status_code')}"
                )
                return None

            # Look for the city-specific rate key: "CityName_1g"
            city_key = f"{city}_{purity}" if metal.lower() == "gold" else f"{city}_1g"

            rate = data.get(city_key)
            if rate is None:
                self.logger.debug(f"No rate found for key: {city_key}")
                return None

            return float(rate)

        except Exception as e:
            self.logger.error(f"Error extracting {metal} rate from response: {e}")
            return None

    def update_bullion_investments(self, db: Session, bullion_data: Dict) -> Dict:
        """Update bullion investment records with current prices.

        Updates all bullion investments in the database with current metal prices,
        recalculating current values, ROI, and XIRR for each investment.

        Args:
            db: Database session
            bullion_data: Dictionary mapping metal names to current prices per gram

        Returns:
            Dictionary with keys:
                - 'success': Boolean indicating overall success
                - 'updated_count': Number of investments successfully updated
                - 'errors': List of error messages (if success=True) or single error (if success=False)
        """

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
                        self.logger.info(
                            f"Updating Bullion investment data for {metal}"
                        )
                        self.logger.info(
                            f"Current price for {metal} in INR: {currency_symbol}{current_price}"
                        )

                        current_value = current_price * investment.quantity_in_grams
                        initial_investment = investment.total_invested_amount

                        # Update current price and calculated fields
                        investment.current_price_per_gram = current_price
                        investment.current_total_value = current_value

                        roi_value = FinancialCalculator.calculate_roi(
                            investment.current_total_value, initial_investment
                        )
                        # Calculate return on investment
                        investment.return_on_investment = roi_value

                        # Calculate XIRR (simplified version) using shared utility
                        investment.xirr = FinancialCalculator.calculate_xirr(
                            current_value,
                            initial_investment,
                            investment.investment_date,
                            today.date(),
                        )

                        updated_count += 1
                        self.logger.debug(
                            f"Updated {metal} investment: ${current_price}"
                        )

                    except Exception as e:
                        self.logger.error(f"Failed to update {metal} investment: {e}")

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} bullion investments")

            return {"success": True, "updated_count": updated_count, "errors": errors}

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update bullion investments: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "updated_count": 0}

    def update_bullion_summary(self, db: Session, bullion_data: Dict) -> Dict:
        """Update bullion summary records with current prices.

        Updates all bullion summary records in the database with current metal prices,
        recalculating aggregated values, ROI, and weighted average XIRR.

        Args:
            db: Database session
            bullion_data: Dictionary mapping metal names to current prices per gram

        Returns:
            Dictionary with keys:
                - 'success': Boolean indicating overall success
                - 'updated_count': Number of summaries successfully updated
                - 'errors': List of error messages (if success=True) or single error (if success=False)
        """
        updated_count = 0
        errors = []

        try:
            for metal, current_price in bullion_data.items():
                # Get all crypto investments that need updating
                bullion_summaries = (
                    db.query(BullionSummary)
                    .filter(BullionSummary.metal_name == metal)
                    .all()
                )
                investments = (
                    db.query(BullionInvestment)
                    .filter(BullionInvestment.metal_name == metal)
                    .all()
                )

                currency_symbol = "₹"
                for summary in bullion_summaries:
                    try:
                        self.logger.info(f"Updating Bullion Summary data for {metal}")
                        self.logger.info(
                            f"Current price for {metal} in INR: {currency_symbol}{current_price}"
                        )

                        current_value = round(
                            (current_price * summary.total_quantity), 2
                        )

                        initial_investment = summary.total_cost
                        roi_value = FinancialCalculator.calculate_roi(
                            current_value, initial_investment
                        )

                        # Weighted average XIRR calculation from Bullion Investment
                        relevant_investments = [
                            inv for inv in investments if inv.metal_name == metal
                        ]

                        if relevant_investments:
                            total_weighted_xirr = sum(
                                (investment.total_invested_amount / initial_investment)
                                * investment.xirr
                                for investment in relevant_investments
                            )
                            self.logger.info(
                                f"Total weighted xirr calculated is: {round(total_weighted_xirr, 2)}%"
                            )
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
                            f"Updated {metal} investment summary with price: {currency_symbol}{current_price}"
                        )

                    except Exception as e:
                        error_msg = (
                            f"Error updating investment summary {summary.id}: {e}"
                        )
                        self.logger.error(error_msg)
                        errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} bullion investment summary")

            return {"success": True, "updated_count": updated_count, "errors": errors}

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update bullion investment summary: {e}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "updated_count": 0}


# Global configuration instance
bullionFetcher = MetalRateFetcher()
