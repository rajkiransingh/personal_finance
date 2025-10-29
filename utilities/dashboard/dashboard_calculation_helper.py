import json

from sqlalchemy.orm import Session

from backend.common.base_fetcher import BaseFetcher
from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import get_portfolio_summary


class DashboardDataCalculator(BaseFetcher):

    def __init__(self):
        self.db: Session = next(get_db())
        self.cache_key_prefix = "dashboard"
        self.summary = "summary"
        self.cache_expiry_in_seconds = 86400

        super().__init__("Dashboard_Data_Fetcher", self.cache_key_prefix, cache_expiry_seconds=86400)
        self.logger.info("Dashboard Calculation class initialized successfully")

    def get_investment_data(self) -> dict:
        """
            Fetch aggregated portfolio-config data across all investment types.

            Returns:
                dict: Aggregated portfolio-config metrics including total invested value,
                      current value, profit/loss, and weighted average ROI.
        """

        # --- Try cache first ---
        cached_map = self.get_from_cache(self.cache_key_prefix, [self.summary])
        cached_info = cached_map.get(self.summary)
        if cached_info:
            self.logger.info("Cache hit :: Dashboard summary loaded from Redis")
            return cached_info

        summary = get_portfolio_summary(self.db)
        total_cost = sum(v["total_cost"] for v in summary.values())
        total_current_value = sum(v["current_value"] for v in summary.values())
        total_returns = total_current_value - total_cost
        weighted_xirr = (
            sum(v["xirr"] * v["total_cost"] for v in summary.values()) / total_cost
            if total_cost else 0
        )

        def safe_get(key, field):
            return round(summary.get(key, {}).get(field, 0), 2)

        # --- Placeholder logic for Cash and Corpus ---
        # TODO: Replace with computed values once income & expenses tracking exists
        total_cash = 250000  # → to be derived from `income - expenses`
        required_six_months_expense = 700000  # → configurable or computed from expense model
        emergency_coverage = (
            round((total_cash / required_six_months_expense) * 100, 2)
            if required_six_months_expense else 0
        )

        assets = {
            "Cash": total_cash,
            "Stocks": safe_get("stocks", "current_value"),
            "Mutual_Fund": safe_get("mutual_funds", "current_value"),
            "Gold": safe_get("gold", "current_value"),
            "Silver": safe_get("silver", "current_value"),
            "Land": safe_get("real_estate", "current_value"),
            "Crypto": safe_get("crypto", "current_value"),
        }

        investment_returns = {
            "Stocks": safe_get("stocks", "xirr"),
            "Mutual_Fund": safe_get("mutual_funds", "xirr"),
            "Gold": safe_get("gold", "xirr"),
            "Silver": safe_get("silver", "xirr"),
            "Land": safe_get("real_estate", "xirr"),
            "Crypto": safe_get("crypto", "xirr"),
        }

        result = {
            "emergency_coverage": emergency_coverage,  # ← replaces 'corpus'
            "total_returns": round(total_returns, 2),
            "average_roi": round(weighted_xirr, 2),
            "assets": assets,
            "investment_returns": investment_returns,
            "spending": {},  # reserved for future use
        }

        try:
            self.redis_client.setex(self.cache_key_prefix, self.cache_expiry_in_seconds, json.dumps(result))
        except Exception as e:
            self.logger.warning(f"Cache write failed for {self.cache_key_prefix}: {e}")

        return result


# Global configuration instance
dashboardDataCalculator = DashboardDataCalculator()
