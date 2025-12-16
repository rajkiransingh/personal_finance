import json
from datetime import datetime, UTC
from decimal import Decimal
from typing import Dict

import requests
from sqlalchemy.orm import Session

from utilities.common.base_fetcher import BaseFetcher
from utilities.common.financial_utils import FinancialCalculator
from backend.models.investments.mutual_fund import MutualFundInvestment, MutualFundSummary


class MutualFundPriceFetcher(BaseFetcher):
    """Utility class to fetch mutual fund prices"""

    def __init__(self):
        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "mutual-fund"

        super().__init__("Mutual_Fund_price_fetcher", self.cache_key_prefix, self.cache_expiry_in_seconds)
        self.logger.info("Mutual Fund price fetcher initialized successfully")

    def get_mutual_fund_rates_bulk(self, scheme_code_list: list):
        """Fetch Mutual Fund NAVs for multiple scheme codes with caching"""
        results = {}
        cached_map = self.get_from_cache(self.cache_key_prefix, scheme_code_list)
        missing_schemes = [scheme for scheme, val in cached_map.items() if val is None]

        if missing_schemes:
            self.logger.info(f"Cache miss for {len(missing_schemes)} mutual fund(s): {missing_schemes}")
            for scheme_code in missing_schemes:
                try:
                    self.logger.info(f"Fetching data from Rapid API for scheme: {scheme_code}")
                    endpoint = f"{self.mf_base_url}{scheme_code}"
                    headers = {
                        'x-rapidapi-host': self.rapid_api_mf_host,
                        'x-rapidapi-key': self.rapid_api_key
                    }

                    response = requests.get(endpoint, headers=headers, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    mf_data = data['data']

                    # Store in cache
                    try:
                        self.set_cache(f"{self.cache_key_prefix}", {scheme_code: mf_data})
                        self.logger.info(f"Cached NAV for {mf_data['Fund_Name']} successfully")
                    except Exception as e:
                        self.logger.warning(f"Failed to cache NAV for {scheme_code}: {e}")

                    results[scheme_code] = mf_data

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Request failed for {scheme_code}: {e}")
                    results[scheme_code] = None
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON for {scheme_code}: {e}")
                    results[scheme_code] = None
                except Exception as e:
                    self.logger.error(f"Unexpected error for {scheme_code}: {e}")
                    results[scheme_code] = None

        # Merge cached and newly fetched data
        for scheme_code, cached_val in cached_map.items():
            if cached_val is not None:
                results[scheme_code] = cached_val

        return results

    def update_bullion_investments(self, db: Session, mf_data: Dict) -> Dict:

        today = datetime.now(UTC)
        updated_count = 0
        errors = []
        try:
            for scheme_code, data in mf_data.items():
                # Get all bullion investments that need updating
                mutual_fund_investments = (
                    db.query(MutualFundInvestment)
                    .filter(MutualFundInvestment.scheme_code == scheme_code,
                            MutualFundInvestment.transaction_type == 'BUY')
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
                        roi_value = FinancialCalculator.calculate_roi(current_value, initial_investment)
                        
                        # Calculate XIRR using shared utility
                        investment.xirr = FinancialCalculator.calculate_xirr(
                            current_value, initial_investment, investment.investment_date, today.date()
                        )

                        # Updating the investment table
                        investment.current_price_per_unit = nav
                        investment.current_total_value = current_value
                        investment.return_on_investment = roi_value

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

                # Get all mutual fund investments that need updating
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
                        roi_value = FinancialCalculator.calculate_roi(current_value, initial_investment)

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
