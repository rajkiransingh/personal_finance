import json
import os
from datetime import datetime, UTC
from decimal import Decimal
from typing import Dict

import requests
from sqlalchemy.orm import Session

from backend.common.setup import AppConfig, config
from backend.models.investments.mutual_fund import MutualFundInvestment, MutualFundSummary


class MutualFundPriceFetcher:
    """Utility class to fetch mutual fund prices"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Mutual_Fund_price_fetcher",
                                             "Mutual_Fund_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        # Initialize env variables
        self.rapid_api_host = os.getenv("RAPID_API_MF_HOST")
        self.base_url = os.getenv("RAPID_API_MF_URL")
        self.rapid_api_key = os.getenv("RAPID_MF_API_KEY")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "mutual-fund:"

        self.currency = {
            1: "₹",  # INR
            2: "zł",  # PLN
            3: "$",  # USD
        }

        self.logger.info("Mutual Fund price fetcher initialized successfully")

    def get_mutual_fund_rates_bulk(self, scheme_code_list: list):
        """Fetch Mutual Fund NAVs for multiple scheme codes with caching"""
        result = {}

        for scheme_code in scheme_code_list:
            cache_key = f"{self.cache_key_prefix}:{scheme_code}"
            cached_data = self.redis_client.get(cache_key)
            cached_info = json.loads(cached_data)

            if cached_info:
                self.logger.info(
                    f"Cache hit: Using cached data for Mutual Fund: {cached_info['Fund_Name']} with value: {cached_info['NAV']}")
                result[scheme_code] = cached_info
                continue

            try:
                self.logger.info(f"Fetching the data from rapid API for scheme code: {scheme_code}")
                endpoint = f"{self.base_url}{scheme_code}"

                headers = {
                    'x-rapidapi-host': self.rapid_api_host,
                    'x-rapidapi-key': self.rapid_api_key
                }

                response = requests.get(endpoint, headers=headers, timeout=30)
                response.raise_for_status()

                data = response.json()
                self.logger.info(
                    f"Fetched {data['data']['Fund_Name']} with scheme code: {scheme_code}:: nav - {data['data']['NAV']}")

                # Store in Redis with a 24-hour expiry
                try:
                    self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(data['data']))
                    self.logger.info(f"Cached mutual fund nav of - {data['data']['Fund_Name']} in Redis")
                except Exception as e:
                    self.logger.warning(f"Failed to cache nav of - {data['data']['Fund_Name']}:: Error - {e}")

                result[scheme_code] = data

            except Exception as e:
                self.logger.error(
                    f"Cache miss: Error fetching Mutual Fund data for scheme code: {scheme_code} Error - {e}")
                result[scheme_code] = None  # Store None for this scheme code

        return result

    def update_bullion_investments(self, db: Session, mf_data: Dict) -> Dict:

        today = datetime.now(UTC)
        updated_count = 0
        errors = []
        try:
            for scheme_code, data in mf_data.items():
                # Get all bullion investments that need updating
                mutual_fund_investments = (
                    db.query(MutualFundInvestment)
                    .filter(MutualFundInvestment.scheme_code == scheme_code)
                    .all()
                )
                nav = Decimal(data['NAV'])
                currency_symbol = "₹"
                for investment in mutual_fund_investments:
                    try:
                        self.logger.info(
                            f"Updating Mutual Fund investment data for {mf_data[scheme_code]['Fund_Name']}")
                        self.logger.info(
                            f"Current price for scheme code: {scheme_code} in INR is: {currency_symbol}{nav}")

                        current_value = float(nav * investment.unit_quantity)
                        initial_investment = investment.total_invested_amount
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Calculate XIRR (simplified version)
                        days_invested = (today.date() - investment.investment_date).days
                        years = days_invested / 365.0

                        # Updating the investment table
                        investment.current_price_per_unit = nav
                        investment.current_total_value = current_value
                        investment.return_on_investment = roi_value
                        investment.xirr = (((current_value / initial_investment) ** (
                                1 / years)) - 1) * 100 if years > 0 else 0.0

                        updated_count += 1
                        self.logger.debug(
                            f"Updated {mf_data[scheme_code]['Fund_Name']}  with nav: {currency_symbol}{nav}")

                    except Exception as e:
                        self.logger.error(f"Failed to update {mf_data[scheme_code]['Fund_Name']} investment: {e}")

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} mutual fund investments")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update mutual fund investments: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }

    def update_bullion_summary(self, db: Session, mf_data: Dict) -> Dict:
        updated_count = 0
        errors = []

        try:
            for scheme_code, data in mf_data.items():
                self.logger.info(f"Received updates for mutual fund data: {mf_data}")

                # Get all crypto investments that need updating
                mf_summaries = db.query(MutualFundSummary).filter(MutualFundSummary.scheme_code == scheme_code).all()
                investments = db.query(MutualFundInvestment).filter(
                    MutualFundInvestment.scheme_code == scheme_code).all()

                nav = float(data['NAV'])
                currency_symbol = "₹"
                for summary in mf_summaries:
                    try:
                        self.logger.info(f"Updating Mutual Fund Summary data for {mf_data[scheme_code]['Fund_Name']}")
                        self.logger.info(
                            f"Current price for scheme code: {scheme_code} in INR is: {currency_symbol}{nav}")

                        current_value = round((nav * summary.total_quantity), 2)

                        initial_investment = summary.total_cost
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Weighted average XIRR calculation from Bullion Investment
                        relevant_investments = [
                            inv for inv in investments if inv.scheme_code == scheme_code
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
                        summary.current_price_per_unit = nav
                        summary.current_value = current_value
                        summary.roi = roi_value
                        summary.xirr = total_weighted_xirr
                        summary.last_updated = datetime.now(UTC)

                        updated_count += 1
                        self.logger.info(
                            f"Updated {mf_data[scheme_code]['Fund_Name']} investment summary with price: {currency_symbol}{nav}")

                    except Exception as e:
                        error_msg = f"Error updating investment summary {summary.id}: {e}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} mutual fund investment summary")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update mutual fund investment summary: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }


# Global configuration instance
mutualFundFetcher = MutualFundPriceFetcher()
