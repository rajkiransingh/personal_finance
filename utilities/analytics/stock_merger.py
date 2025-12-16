import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import process, fuzz
from sqlalchemy.orm import Session

from utilities.common.base_fetcher import BaseFetcher
from backend.models.investments.analytics import StocksValuableData, StockList
from backend.services.db_services import get_db
from utilities.analytics.sector_mapping import SECTOR_MAP

ROOT_DIR = Path(__file__).resolve().parents[2]
FILE_LOCATION = ROOT_DIR / 'backend' / 'files' / 'stocks'
ALL_STOCKS_CSV = os.path.join(FILE_LOCATION, "All_Stocks_List.csv")
NIFTY_500_CSV = os.path.join(FILE_LOCATION, "NIFTY_500_Stocks_List.csv")
OUTPUT_CSV = os.path.join(FILE_LOCATION, "Merged_List_of_500_Stocks.csv")
TICKER_TAPE_CSV = os.path.join(FILE_LOCATION, "Ticker_Tape_Data.csv")
FINAL_OUTPUT_CSV = os.path.join(FILE_LOCATION, "Final_Merged_List_of_500_Stocks.csv")


def enrich_with_sector(df: pd.DataFrame) -> pd.DataFrame:
    """Map sub-sectors to major sectors."""
    df["sector"] = df["sub-sector"].map(SECTOR_MAP).fillna("Unknown")
    return df


def normalize_company_name(name):
    """Normalize company name for better matching."""
    if pd.isna(name):
        return ""
    name = str(name).lower()
    # Remove common suffixes and extra whitespace
    replacements = [
        'limited', 'ltd', 'ltd.', 'pvt', 'pvt.', 'private',
        'corporation', 'corp', 'inc', 'incorporated', '(I)', 'India'
    ]
    for word in replacements:
        name = name.replace(word, '')
    name.replace('&', 'and')
    return ' '.join(name.split()).strip()


def clean_numeric_value(value):
    """Convert placeholder values to None, remove commas, convert to float."""
    if value is None or pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        value = value.strip()
        # Check for placeholder values
        if value in ['-', '--', 'N/A', 'NA', 'n/a', '', 'null']:
            return None

        # Remove commas and convert to float
        try:
            # Remove commas and any other non-numeric characters except . and -
            cleaned = value.replace(',', '').replace('%', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    return value


def _build_extra_metrics(row):
    """Build nested JSON metrics structure for DB insertion."""

    def val(key): return clean_numeric_value(row.get(key))

    return {
        "growth": {
            "eps_growth_1y": val("1y historical eps growth"),
            "eps_growth_5y": val("5y historical eps growth"),
            "revenue_growth_1y": val("1y historical revenue growth"),
            "revenue_growth_5y": val("5y historical revenue growth"),
            "200_days_ema": val("200d ema"),
            "200_days_sma": val("200d sma"),
            "total_revenue": val("total revenue"),
        },

        "valuation": {
            "price_to_sales": val("price / sales"),
            "price_to_cfo": val("price / cfo"),
            "ev_ebitda": val("ev/ebitda ratio"),
            "book_value": val("book value"),
            "pe_ratio": val("pe ratio"),
            "pb_ratio": val("pb ratio"),
            "sector_pe": val("sector pe"),
            "sector_pb": val("sector pb"),
            "sector_dividend_yield": val("sector dividend yield"),
            "total_assets": val("total assets"),
            "enterprise_value": val("enterprise value"),
        },

        "profitability": {
            "roi": val("return on investment"),
            "net_profit_margin": val("net profit margin"),
            "ebitda_margin": val("ebitda margin"),
            "earning_power": val("earning power"),
            "ebitda": val("ebitda"),
            "eps": val("earnings per share"),
            "net_income": val("net income"),
            "asset_turnover_ratio": val("asset turnover ratio"),
            "5y_avg_ebitda_margin": val("5y average ebitda margin"),
            "5y_cagr": val("5y cagr"),
        },

        "ownership": {
            "promoter_holding": val("promoter holding"),
            "promoter_holding_change_3m": val("promoter holding change\xa0–\xa03m"),
            "dii_holding": val("domestic institutional holding"),
            "fii_holding": val("foreign institutional holding"),
        },

        "liquidity": {
            "quick_ratio": val("quick ratio"),
            "current_ratio": val("current ratio"),
            "interest_coverage_ratio": val("interest coverage ratio"),
            "debt_to_equity": val("debt to equity"),
            "total_debt": val("total debt"),
            "free_cash_flow": val("free cash flow"),
            "financing_cash_flow": val("financing cash flow"),
            "cash_flow_margin": val("cash flow margin"),
            "operating_cash_flow": val("operating cash flow"),
        },

        "market": {
            "dividend_yield": val("dividend yield"),
            "sharpe_ratio": val("sharpe ratio"),
            "1m_return": val("1m return"),
            "1d_return": val("1d return"),
        }
    }


class StockMerger(BaseFetcher):
    def __init__(self):
        # Load config data from environment
        self.cache_expiry_in_seconds = 86400 * 30
        self.cache_key_prefix = "stock_merge"

        super().__init__("Stock_Merger", self.cache_key_prefix, self.cache_expiry_in_seconds)
        self.logger.info("Stock merger initialized successfully")
        self.db: Session = next(get_db())

    def is_recently_modified(self, file_path, hours=48):
        """Check if a file was modified in the last XX hours."""
        if not os.path.exists(file_path):
            self.logger.info("❌ Missing CSV Files.")
            return False

        mod_time = os.path.getmtime(file_path)
        self.logger.info("✅ Last modified: %s", datetime.fromtimestamp(mod_time))
        return (datetime.now() - datetime.fromtimestamp(mod_time)).total_seconds() < hours * 3600

    def _load_and_normalize_data(self):
        self.logger.info("🔄 Reading Ticker & Top 500 Stocks CSV files...")
        merged_list = pd.read_csv(OUTPUT_CSV)
        ticker_data = pd.read_csv(TICKER_TAPE_CSV)

        # Normalize column names
        merged_list.columns = merged_list.columns.str.strip().str.lower()
        ticker_data.columns = ticker_data.columns.str.strip().str.lower()

        self.logger.info("📊 Merged list columns: %s", merged_list.columns.tolist())
        self.logger.info("📊 Ticker data columns: %s", ticker_data.columns.tolist())

        # Enrich ticker data with Sector mapping
        ticker_data = enrich_with_sector(ticker_data)

        # Create normalized name columns
        merged_list['normalized_name'] = merged_list['name of company'].apply(normalize_company_name)
        ticker_data['normalized_name'] = ticker_data['name'].apply(normalize_company_name)

        return merged_list, ticker_data

    def _merge_dataframes(self, merged_list, ticker_data):
        final_df = pd.merge(
            merged_list,
            ticker_data,
            on="normalized_name",
            how="left",
            suffixes=("", "_ticker")
        )

        unmatched_mask = final_df["name"].isna()
        if unmatched_mask.sum() > 0:
            self.logger.info(f"🔍 Fuzzy matching {unmatched_mask.sum()} unmatched...")
            ticker_names = ticker_data["normalized_name"].tolist()
            for idx in final_df[unmatched_mask].index:
                query = final_df.loc[idx, "normalized_name"]
                if not query:
                    continue
                match = process.extractOne(query, ticker_names, scorer=fuzz.token_sort_ratio, score_cutoff=80)
                if match:
                    best_name, score, _ = match
                    ticker_row = ticker_data[ticker_data["normalized_name"] == best_name].iloc[0]
                    for col in ticker_data.columns:
                        if col != "normalized_name" and col in final_df.columns:
                            final_df.loc[idx, col] = ticker_row[col]
                    self.logger.info(f" ✓ {query} → {best_name} (score {score})")

        final_df.drop(columns=["normalized_name"], errors="ignore", inplace=True)
        return final_df

    def _save_and_log_merge(self, final_df):
        matched = final_df['name'].notna().sum()
        total = len(final_df)
        self.logger.info(f"✅ Matched {matched}/{total} records ({(matched / total) * 100:.1f}%)")

        # Save to CSV as reference
        final_df.to_csv(FINAL_OUTPUT_CSV, index=False)
        self.logger.info(f"📁 Saved enriched CSV: {FINAL_OUTPUT_CSV}")

        # Show sample of unmatched companies
        unmatched = final_df[final_df['name'].isna()]['name of company'].head(10)
        if not unmatched.empty:
            self.logger.info("🔍 Sample unmatched companies:")
            for name in unmatched:
                self.logger.info(f"  - {name}")

    def _insert_into_database(self, final_df, db: Session):
        final_df = final_df.replace({np.nan: None, 'nan': None, 'NaN': None})
        stocks_added = stocks_updated = valuable_added = 0
        errors = []

        for idx, row in final_df.iterrows():
            try:
                symbol = row.get("symbol")
                company_name = row.get("name of company")
                name = row.get("name")
                if not symbol or pd.isna(symbol):
                    errors.append(f"Row {idx}: Missing symbol (Name: {row.get('name of company', 'Unknown')})")
                    continue

                if not name or pd.isna(name):
                    self.logger.warning(f"Row {idx}: Symbol {symbol} has no ticker data match, skipping valuable data")

                if symbol == "NIFTY 500":
                    self.logger.info(f"Skipping index entry: {symbol}")
                    continue

                stock = db.query(StockList).filter_by(symbol=symbol).first()
                if not stock:
                    stock = StockList(
                        symbol=symbol,
                        name=company_name,
                        sector=row.get("sector") or "Unknown",
                        sub_sector=row.get("sub-sector") or "Unknown",
                        is_active=True,
                        last_updated=datetime.now()
                    )
                    db.add(stock)
                    stocks_added += 1
                else:
                    if company_name and (not stock.name or stock.name == "Unknown"):
                        stock.name = company_name
                    stock.sector = row.get("sector") or stock.sector
                    stock.sub_sector = row.get("sub-sector") or stock.sub_sector
                    stock.last_updated = datetime.now()
                    stocks_updated += 1

                if name:
                    today = datetime.now().date()
                    existing = db.query(StocksValuableData).filter_by(symbol=symbol, date=today).first()
                    metrics = _build_extra_metrics(row)
                    eps_growth = clean_numeric_value(row.get("1y historical eps growth"))
                    pe = clean_numeric_value(row.get("pe ratio"))
                    peg = (pe / eps_growth) if eps_growth and eps_growth > 0 else None

                    if existing:
                        existing.market_cap = clean_numeric_value(row.get("↓market cap"))
                        existing.close_price = clean_numeric_value(row.get("close price"))
                        existing.pe_ratio = pe
                        existing.pb_ratio = clean_numeric_value(row.get("pb ratio"))
                        existing.peg_ratio = peg
                        existing.roe = clean_numeric_value(row.get("return on equity"))
                        existing.roce = clean_numeric_value(row.get("roce"))
                        existing.debt_to_equity = clean_numeric_value(row.get("debt to equity"))
                        existing.promoter_holding = clean_numeric_value(row.get("promoter holding"))
                        existing.ebitda_margin = clean_numeric_value(row.get("ebitda margin"))
                        existing.ev_ebitda = clean_numeric_value(row.get("ev/ebitda ratio"))
                        existing.extra_metrics = metrics
                        existing.updated_flag = True
                        existing.last_updated = datetime.now()
                    else:
                        valuable = StocksValuableData(
                            symbol=symbol,
                            sector=row.get("sector") or "Unknown",
                            sub_sector=row.get("sub-sector") or "Unknown",
                            date=today,
                            market_cap=clean_numeric_value(row.get("↓market cap")),
                            close_price=clean_numeric_value(row.get("close price")),
                            pe_ratio=pe,
                            pb_ratio=clean_numeric_value(row.get("pb ratio")),
                            peg_ratio=peg,
                            roe=clean_numeric_value(row.get("return on equity")),
                            roce=clean_numeric_value(row.get("roce")),
                            debt_to_equity=clean_numeric_value(row.get("debt to equity")),
                            promoter_holding=clean_numeric_value(row.get("promoter holding")),
                            ebitda_margin=clean_numeric_value(row.get("ebitda margin")),
                            ev_ebitda=clean_numeric_value(row.get("ev/ebitda ratio")),
                            extra_metrics=metrics,
                            updated_flag=True,
                            created_at=datetime.now(),
                            last_updated=datetime.now(),
                        )
                        db.add(valuable)
                        valuable_added += 1

            except Exception as e:
                errors.append(f"Row {idx} ({symbol}): {str(e)}")

        db.commit()
        self.logger.info(
            f"\n✅ DB update done | Added: {stocks_added}, Updated: {stocks_updated}, Valuable: {valuable_added}")
        if errors:
            self.logger.error(f"⚠️ Errors: {len(errors)} (showing 10)")
            for err in errors[:10]:
                self.logger.error(f"  - {err}")

    def merge_stock_lists(self):
        """Merge All_stocks_list and 500_stocks_list to create final 500 stock symbol-name mapping."""
        # Check modification timestamps
        if not (self.is_recently_modified(ALL_STOCKS_CSV) or self.is_recently_modified(NIFTY_500_CSV)):
            self.logger.info("⚙️  No changes in top 500 stock list or base stocks list. Skipping merge.")
            return

        self.logger.info("🔄 Reading new stocks CSV files...")
        all_stocks = pd.read_csv(ALL_STOCKS_CSV)
        nifty_500 = pd.read_csv(NIFTY_500_CSV)

        # Normalize column names
        all_stocks.columns = all_stocks.columns.str.strip().str.upper()
        nifty_500.columns = nifty_500.columns.str.strip().str.upper()

        # Merge based on SYMBOL
        merged = pd.merge(
            nifty_500, all_stocks,
            on="SYMBOL",
            how="left"
        )

        keep_cols = ["SYMBOL", "NAME OF COMPANY", "ISIN NUMBER", "DATE OF LISTING", "FACE VALUE"]
        merged = merged[[col for col in keep_cols if col in merged.columns]]

        self.logger.info(f"✅ Merged {len(merged)} records. Saving output...")
        merged.to_csv(OUTPUT_CSV, index=False)
        self.logger.info(f"📁 Saved: {OUTPUT_CSV}")

    def merge_with_ticker_data(self, db: Session):
        """Merge merged stock list with Tickertape data and push to DB."""

        # Check modification timestamps
        if not (self.is_recently_modified(TICKER_TAPE_CSV) or self.is_recently_modified(OUTPUT_CSV)):
            self.logger.info("⚙️  No changes in Ticker & Top 500 stocks CSVs. Skipping merge.")
            return None

        merged_list, ticker_data = self._load_and_normalize_data()

        self.logger.info("🔄 Merging and enriching data...")
        final_df = self._merge_dataframes(merged_list, ticker_data)
        self._save_and_log_merge(final_df)

        self.logger.info("\n💾 Starting database insertion...")
        self._insert_into_database(final_df, db)

        return final_df


# Global configuration instance
stockMerger = StockMerger()
