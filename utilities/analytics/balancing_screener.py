from datetime import datetime, date
from pathlib import Path
from typing import Tuple, Dict, Any

from sqlalchemy.orm import Session

from utilities.common.base_fetcher import BaseFetcher
from backend.services.db_services import get_db
from utilities.common.config_loader_util import load_config, save_config
from utilities.common.value_extractor_util import (
    round2,
    sum_current_values,
    extract_current_value,
)
from utilities.fetch_overall_investment_data import get_investments_with_sub_allocations


class BalancingScreener(BaseFetcher):
    def __init__(self):
        """Initialize balancing screener with database and cache configuration.

        Sets up the screener with database session, cache configuration for
        rebalancing calculations, and initializes the base fetcher.
        """
        self.db: Session = next(get_db())
        self.cache_key_prefix = "rebalancing_screener"
        self.cache_expiry_in_seconds = 86400
        super().__init__(
            "utilities.analytics.balancing_screener",
            self.cache_key_prefix,
            self.cache_expiry_in_seconds,
        )
        self.logger.debug("Balancing screener initialized")

    # ---------------------------------------------------------------
    # Aggregate Portfolio Values
    # ---------------------------------------------------------------
    def get_total_and_categories(
        self, portfolio_config: dict, portfolio_data: dict = None
    ) -> Tuple[float, Dict[str, Any]]:
        """Aggregate total and per-category investment values."""

        if not portfolio_data:
            self.logger.warning("No portfolio data received; returning empty results.")
            return 0.0, {}

        cat_values, total_value = {}, 0.0
        mappings = portfolio_config.get("mappings", {})

        # Define local helper for symbol/name matching
        def match_and_sum(sub_name, mapped_symbols=None) -> Tuple[bool, float]:
            sub_norm = sub_name.lower().replace(" ", "")
            matched_sum, matched_any = 0.0, False

            for category, entries in portfolio_data.items():
                if not entries:
                    continue

                for e in entries:
                    # Extract name and symbol correctly
                    if isinstance(e, dict):
                        e_name = (
                            e.get("metal_name")
                            or e.get("stock_name")
                            or e.get("fund_name")
                            or e.get("name")
                            or ""
                        ).lower()
                        e_symbol = (
                            e.get("symbol")
                            or e.get("stock_symbol")
                            or e.get("fund_symbol")
                            or ""
                        ).lower()
                        cur_val = e.get("current_value", 0.0)
                    else:
                        e_name = (
                            getattr(e, "metal_name", None)
                            or getattr(e, "stock_name", None)
                            or getattr(e, "fund_name", None)
                            or getattr(e, "name", None)
                            or ""
                        )
                        e_symbol = (
                            getattr(e, "symbol", None)
                            or getattr(e, "stock_symbol", None)
                            or getattr(e, "fund_symbol", None)
                            or ""
                        )
                        e_name = str(e_name).lower()
                        e_symbol = str(e_symbol).lower()
                        cur_val = extract_current_value(e)

                    # If mapped_symbols exist, check direct symbol match first
                    if mapped_symbols and e_symbol.upper() in [
                        s.upper() for s in mapped_symbols
                    ]:
                        matched_sum += float(cur_val)
                        matched_any = True
                        continue

                    # If sub_name matches metal_name exactly for bullion, take it
                    if "gold" in sub_norm or "silver" in sub_norm:
                        if e_name == sub_norm:  # exact match on metal_name
                            matched_sum += float(cur_val)
                            matched_any = True
                            continue

                    # fallback fuzzy match for other categories
                    if sub_norm in e_name.replace(
                        " ", ""
                    ) or sub_norm in e_symbol.replace(" ", ""):
                        matched_sum += float(cur_val)
                        matched_any = True

            return matched_any, matched_sum

        # Compute values per category
        for cat, cat_info in portfolio_config.get("targets", {}).items():
            mapped_keys = mappings.get(cat, [cat])
            parent_val = sum(
                sum_current_values(portfolio_data.get(k))
                for k in mapped_keys
                if k in portfolio_data
            )

            sub_values, any_sub_matched = {}, False
            for sub_name, _ in cat_info.get("sub_allocations", {}).items():
                sub_map = mappings.get(sub_name, [sub_name])
                is_symbol_list = isinstance(sub_map, list) and all(
                    isinstance(x, str) and x.isupper() for x in sub_map
                )

                if is_symbol_list:
                    found, value = match_and_sum(sub_name, sub_map)
                else:
                    found, value = match_and_sum(sub_name)

                sub_values[sub_name] = float(value)
                if found:
                    any_sub_matched = True

            current_val = sum(sub_values.values()) if any_sub_matched else parent_val
            cat_values[cat] = float(current_val)
            cat_values[f"{cat}_subs"] = sub_values
            total_value += current_val

        return total_value, cat_values

    # ---------------------------------------------------------------
    # Apply Step-Up Logic
    # ---------------------------------------------------------------
    def apply_step_up_if_due(self, config_path="portfolio_config.json") -> float:
        cfg = load_config(config_path)
        step = cfg.get("step_up", {})
        today = date.today()

        if not step.get("enabled"):
            return float(cfg["monthly_sip"])

        last_applied = cfg.get("last_stepup_applied")
        rate = float(step.get("annual_rate", 0))
        due_month, due_day = step.get("apply_month"), step.get("apply_day")

        if today.month == due_month and today.day >= due_day:
            last_date = (
                datetime.fromisoformat(last_applied).date() if last_applied else None
            )
            if not last_date or last_date.year < today.year:
                years = today.year - (last_date.year if last_date else today.year - 1)
                new_val = float(cfg["monthly_sip"]) * ((1 + rate) ** years)
                cfg["monthly_sip"] = round2(new_val)
                cfg["last_stepup_applied"] = today.isoformat()
                save_config(cfg, config_path)
                return new_val
        return float(cfg["monthly_sip"])

    # ---------------------------------------------------------------
    # Compute Allocation Suggestions
    # ---------------------------------------------------------------
    def compute_allocation_suggestion(self, cfg, total_value, cat_values):
        """Compare current vs ideal allocation and propose rebalance."""
        soft, hard = (
            cfg["rebalancing"]["soft_threshold_pct"],
            cfg["rebalancing"]["hard_threshold_pct"],
        )

        result = {
            "total_value": round2(total_value),
            "categories": {},
            "summary": {},
            "next_monthly_sip": cfg["monthly_sip"],
        }

        total_gap_pos = total_gap_neg = 0.0

        for cat, data in cfg.get("targets", {}).items():
            weight = data["weight"]
            current_val = cat_values.get(cat, 0.0)
            ideal_val = total_value * weight
            gap = ideal_val - current_val
            curr_pct = (current_val / total_value * 100) if total_value else 0.0
            target_pct = weight * 100
            drift_pct = (curr_pct - target_pct) / 100

            status = (
                "Significant drift"
                if abs(drift_pct) > hard
                else "Drifted"
                if abs(drift_pct) > soft
                else "OK"
            )

            total_gap_pos += max(0, gap)
            total_gap_neg += max(0, -gap)

            subs = {}
            for sub, sub_wt in data.get("sub_allocations", {}).items():
                sub_cur = cat_values.get(f"{cat}_subs", {}).get(sub, 0.0)
                sub_ideal = ideal_val * sub_wt
                subs[sub] = {
                    "current_value": round2(sub_cur),
                    "ideal_value": round2(sub_ideal),
                    "gap": round2(sub_ideal - sub_cur),
                    "target_pct_of_total": round2(weight * sub_wt * 100),
                }

            result["categories"][cat] = {
                "current_value": round2(current_val),
                "ideal_value": round2(ideal_val),
                "gap": round2(gap),
                "current_pct": round2(curr_pct),
                "target_pct": round2(target_pct),
                "status": status,
                "sub_allocations": subs,
            }

        # Summary & Plan
        result["summary"] = {
            "positive_gap_total": round2(total_gap_pos),
            "negative_gap_total": round2(total_gap_neg),
            "inflow_sufficient": total_gap_pos <= cfg["monthly_sip"],
        }

        if total_gap_pos > 0:
            result["rebalance_plan"] = {
                cat: round2((info["gap"] / total_gap_pos) * cfg["monthly_sip"])
                if info["gap"] > 0
                else 0
                for cat, info in result["categories"].items()
            }

        return result

    # ---------------------------------------------------------------
    # Main Runner
    # ---------------------------------------------------------------
    def run_cycle(self, portfolio_data=None):
        """Run full rebalancing pipeline."""
        base_dir = Path(__file__).resolve().parents[2]
        config_path = base_dir / "frontend" / "portfolio-config.json"

        portfolio_config = load_config(str(config_path))
        portfolio_data = portfolio_data or get_investments_with_sub_allocations(self.db)

        total, cats = self.get_total_and_categories(portfolio_config, portfolio_data)
        self.apply_step_up_if_due(str(config_path))
        return self.compute_allocation_suggestion(portfolio_config, total, cats)


# Global instance
balancingScreener = BalancingScreener()
