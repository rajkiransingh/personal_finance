import json
import os
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.common.base_fetcher import BaseFetcher
from backend.services.db_services import get_db

METRIC_NAME_MAP = {
    "market_cap": "MarketCap",
    "pe_ratio": "PE",
    "pb_ratio": "PB",
    "roe": "ROE",
    "roce": "ROCE",
    "debt_to_equity": "DebtToEquity",
    "promoter_holding": "PromoterHolding",
    "ebitda_margin": "EBITDA_Margin",
    "ev_ebitda": "EV_EBITDA",
    "close_price": "ClosePrice",
}

EXTRA_METRIC_MAP = {
    # Liquidity
    "liquidity_current_ratio": "CurrentRatio",
    "liquidity_quick_ratio": "QuickRatio",
    "liquidity_debt_to_equity": "DebtToEquity",
    "liquidity_interest_coverage_ratio": "InterestCoverage",

    # Profitability
    "profitability_ebitda_margin": "EBITDA_Margin",
    "profitability_net_profit_margin": "NPM",
    "profitability_earning_power": "EarningPower",
    "profitability_roi": "ROI",
    "profitability_eps": "EPS",
    "profitability_ebitda": "EBITDA",

    # Market
    "market_dividend_yield": "DividendYield",
    "market_sharpe_ratio": "SharpeRatio",
    "market_price_to_sales": "PriceToSales",
    "market_1d_return": "1DReturn",
    "market_1m_return": "1MReturn",

    # Valuation
    "valuation_pe_ratio": "PE",
    "valuation_pb_ratio": "PB",
    "valuation_ev_ebitda": "EV_EBITDA",
    "valuation_price_to_cfo": "PriceToCFO",
    "valuation_sector_pb": "sector_pb",
    "valuation_sector_pe": "sector_pe",
    "valuation_book_value": "book_value",
    "valuation_price_to_sales": "price_to_sales",
    "valuation_sector_dividend_yield": "sector_dividend_yield",

    # Ownership
    "ownership_promoter_holding": "PromoterHolding",
    "ownership_promoter_holding_change_3m": "PromoterHoldingChange3M",
    "ownership_dii_holding": "DII_Holding",
    "ownership_fii_holding": "FII_Holding",
}


def flatten_json(data, parent_key="", sep="_"):
    """Recursively flattens nested dicts."""
    items = {}
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def compute_sector_metrics(df: pd.DataFrame):
    """
        Compute mean and std deviation for numeric columns grouped by sector.
        Returns a MultiIndex DataFrame where:
            index -> sector
            columns -> (metric, ['mean', 'std'])
        """
    numeric_cols = df.select_dtypes(include=["number"]).columns
    sector_metrics = (
        df.groupby("sector")[numeric_cols]
        .agg(["mean", "std"])
        .fillna(0.0)
    )
    return sector_metrics


def calculate_strategy_scores(normalized_df, strategies, original_df=None):
    """
    Calculates overall scores and merges real fundamentals if provided.
    """
    results = []

    for _, row in normalized_df.iterrows():
        stock_data = {k.lower(): v for k, v in row.items()}  # normalize keys to lowercase
        stock_symbol = row.get("symbol", "")
        stock_sector = row.get("sector", "")
        stock_subsector = row.get("sub_sector", "")
        stock_scores = {}

        for strat_name, strat_info in strategies.items():
            metrics = strat_info.get("metrics", {})
            total_score = 0.0
            total_weight = 0.0

            aliases = {
                "pb": ["pb_ratio"],
                "pe": ["pe_ratio"],
                "marketcap": ["market_cap"],
                "peg": ["peg_ratio"]
            }

            for metric, weight in metrics.items():
                metric_l = metric.lower().replace("_", "")
                val = None
                for key in stock_data.keys():
                    key_clean = key.replace("_", "").lower()
                    if key_clean == metric_l or key_clean in aliases.get(metric_l, []):
                        val = stock_data[key]
                        break

                if isinstance(val, (int, float)) and not pd.isna(val):
                    total_score += val * weight
                    total_weight += abs(weight)

            final_score = total_score / total_weight if total_weight != 0 else 0.0
            stock_scores[strat_name] = final_score

        results.append({
            "symbol": stock_symbol,
            "sector": stock_sector,
            "sub_sector": stock_subsector,
            **stock_scores
        })

    # Convert to DataFrame
    scores_df = pd.DataFrame(results)

    # ✅ Merge back real (non-normalized) fundamentals
    if original_df is not None:
        merge_cols = ["symbol", "sector", "sub_sector",
                      "market_cap", "pe_ratio", "pb_ratio", "peg_ratio",
                      "roe", "roce", "debt_to_equity", "promoter_holding",
                      "ebitda_margin", "ev_ebitda"]

        raw_subset = original_df[merge_cols].copy()

        # ✅ Remove duplicates before merge
        scores_df = scores_df.drop_duplicates(subset=["symbol", "sector", "sub_sector"])
        raw_subset = raw_subset.drop_duplicates(subset=["symbol", "sector", "sub_sector"])

        merged_df = scores_df.merge(
            raw_subset, on=["symbol", "sector", "sub_sector"], how="left"
        )
        return merged_df

    return scores_df


ROOT_DIR = Path(__file__).resolve().parents[2]
FILE_LOCATION = ROOT_DIR / 'frontend'


class StockAnalysis(BaseFetcher):
    def __init__(self):
        # Load config data from environment
        self.cache_expiry_in_seconds = 86400 * 30
        self.cache_key_prefix = "stock_scores_v1"

        super().__init__("Stock_analysis", self.cache_key_prefix, self.cache_expiry_in_seconds)
        self.logger.info("Stock analysis initialized successfully")

        self.strategy_file = os.path.join(FILE_LOCATION, "stock-score-config.json")
        self.db: Session = next(get_db())

    def fetch_data_from_cache(self, stock_score_key: list):
        return self.get_from_cache(self.cache_key_prefix, stock_score_key)

    def load_strategy(self):
        with open(self.strategy_file, "r") as f:
            return json.load(f)["strategy"]

    def fetch_data(self):
        """Fetches valuable stock data, flattens JSON, and returns a clean DataFrame."""
        from sqlalchemy import text

        query = text("""
            SELECT *
            FROM (
                SELECT
                    symbol, sector, sub_sector, market_cap, pe_ratio, pb_ratio,
                    peg_ratio, roe, roce, debt_to_equity, promoter_holding,
                    ebitda_margin, ev_ebitda, extra_metrics,
                    created_at,
                    ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY created_at DESC) AS rn
                FROM stocks_valuable_data
            ) t
            WHERE rn = 1
        """)

        df = pd.read_sql(query, self.db.bind)

        # Prepare list to hold processed rows
        rows = []

        for _, r in df.iterrows():
            row_dict = {
                "symbol": r["symbol"],
                "sector": r["sector"],
                "sub_sector": r["sub_sector"],
                "market_cap": r["market_cap"],
                "pe_ratio": r["pe_ratio"],
                "pb_ratio": r["pb_ratio"],
                "peg_ratio": r["peg_ratio"],
                "roe": r["roe"],
                "roce": r["roce"],
                "debt_to_equity": r["debt_to_equity"],
                "promoter_holding": r["promoter_holding"],
                "ebitda_margin": r["ebitda_margin"],
                "ev_ebitda": r["ev_ebitda"],
            }

            # Safely parse the JSON field
            try:
                if isinstance(r["extra_metrics"], str):
                    extra = json.loads(r["extra_metrics"])
                elif isinstance(r["extra_metrics"], dict):
                    extra = r["extra_metrics"]
                else:
                    extra = {}
            except Exception as e:
                self.logger.error("⚠️ Failed to parse extra_metrics for {} : {}", r['symbol'], e)
                extra = {}

            # Flatten nested metrics (e.g. liquidity_current_ratio)
            extra_flat = flatten_json(extra)

            # Map to clean names
            for old_key, new_key in EXTRA_METRIC_MAP.items():
                if old_key in extra_flat:
                    row_dict[new_key] = extra_flat[old_key]

            # Add all remaining extra fields (unmapped)
            for k, v in extra_flat.items():
                if k not in EXTRA_METRIC_MAP:
                    row_dict[k] = v

            rows.append(row_dict)

        # Convert to DataFrame
        final_df = pd.DataFrame(rows)

        # Replace NaN or None with 0.0 for numeric processing
        final_df = final_df.fillna(0.0)

        return final_df

    def normalize_within_sector(self, df, sector_metrics, output_file=None):
        """
        Normalize numeric metrics within each sector using z-score normalization.
        """
        df["sector"] = df["sector"].astype(str).str.strip()
        sector_metrics.index = sector_metrics.index.map(lambda x: str(x).strip())

        norm_rows = []

        for _, row in df.iterrows():
            sector = row.get("sector")
            if sector not in sector_metrics.index:
                continue

            norm_row = row.copy()
            sector_data = sector_metrics.loc[sector]

            # Iterate over each metric in the MultiIndex columns
            for col in sector_data.index.levels[0]:
                if col not in df.columns:
                    continue

                mean_val = sector_data[(col, "mean")]
                std_val = sector_data[(col, "std")] or 1.0

                val = row.get(col, 0.0)
                if pd.notnull(val):
                    norm_row[col] = (val - mean_val) / std_val
                else:
                    norm_row[col] = 0.0

            norm_rows.append(norm_row)

        norm_df = pd.DataFrame(norm_rows)

        if output_file:
            norm_df.to_json(output_file, orient="records")

        if norm_df.empty:
            self.logger.warning("⚠️ Warning: Normalized dataframe is empty — check sector matching.")
        else:
            self.logger.info(f"✅ Normalized {len(norm_df)} rows across {norm_df['sector'].nunique()} sectors")

        return norm_df, sector_metrics


# Global configuration instance
stockAnalysis = StockAnalysis()


def get_stock_score():
    cached_info = stockAnalysis.fetch_data_from_cache(["TOP_500_STOCKS"])
    fundamental_fields = [
        "market_cap", "pe_ratio", "pb_ratio", "peg_ratio", "roe", "roce",
        "debt_to_equity", "eps", "ebitda_margin"
    ]

    if cached_info['TOP_500_STOCKS'] is not None:
        stockAnalysis.logger.info(f"Cache hit: Using cached Top_500_Stocks scores")
        return cached_info['TOP_500_STOCKS']

    # Loading data from Json and DB
    strategy = stockAnalysis.load_strategy()
    df = stockAnalysis.fetch_data()

    # Segregating data based on sector and normalizing it
    sector_metrics = compute_sector_metrics(df)
    normalized_df, sector_stats = stockAnalysis.normalize_within_sector(df, sector_metrics)

    # Calculating the overall score for a stock
    result_df = calculate_strategy_scores(normalized_df, strategy, original_df=df)
    result = json.loads(result_df.to_json(orient="records"))
    cache_key = stockAnalysis.cache_key_prefix + "::TOP_500_STOCKS"
    serialized = json.dumps(result)
    stockAnalysis.redis_client.setex(cache_key, stockAnalysis.cache_expiry_in_seconds, serialized)
    stockAnalysis.logger.info(f"Cached Top_500_Stocks scores in Redis")
    return result
