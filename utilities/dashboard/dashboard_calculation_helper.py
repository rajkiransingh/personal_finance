import json
from collections import defaultdict
from datetime import datetime, date
from typing import Union, Any

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import case

from backend.models.earnings.income import Income
from backend.models.investments.bullion import BullionInvestment
from backend.models.investments.crypto import CryptoInvestment
from backend.models.investments.mutual_fund import MutualFundInvestment
from backend.models.investments.real_estate import RealEstateInvestment
from backend.models.investments.stock import StockInvestment
from backend.models.spendings.expense import Expense, ExpenseCategory
from backend.services.db_services import get_db
from utilities.common.base_fetcher import BaseFetcher
from utilities.fetch_overall_investment_data import get_portfolio_summary


def _db_dialect_name(db: Session) -> str:
    """Return the dialect name for the given SQLAlchemy Session."""
    try:
        bind = db.get_bind()
    except SQLAlchemyError:
        bind = getattr(db, "bind", None)
    if bind is None:
        return "sqlite"
    return bind.dialect.name.lower()


def _resolve_converted_column(Model, converted_amount: Union[str, Any]):
    """
    Accept either:
      - a SQL expression (e.g. case(...) returned by get_converted_amount)
      - or a string attribute name present on Model (e.g. 'converted_amount')
    Return a SQLAlchemy column/expression to use in queries.
    """
    if isinstance(converted_amount, str):
        return getattr(Model, converted_amount)
    return converted_amount


def get_ytd_sum(db, model, converted_amount, date_field, year_start, today):
    """Get year-to-date sum with currency conversion."""
    col = _resolve_converted_column(model, converted_amount)
    total = (
        db.query(func.sum(col))
        .filter(
            getattr(model, date_field) >= year_start,
            getattr(model, date_field) <= today,
        )
        .scalar()
    )
    return float(total or 0.0)


def get_last_year_sum(
        db, model, converted_amount, date_field, last_year_start, last_year_today
):
    """Get last year same period sum with currency conversion."""
    col = _resolve_converted_column(model, converted_amount)
    total = (
        db.query(func.sum(col))
        .filter(
            getattr(model, date_field) >= last_year_start,
            getattr(model, date_field) <= last_year_today,
        )
        .scalar()
    )
    return float(total or 0.0)


def calculate_change(current, previous):
    """Calculate percentage change. Returns 0.0 if previous <= 0."""
    try:
        return ((current - previous) / previous) * 100 if previous > 0 else 0.0
    except Exception:
        return 0.0


# --- helper: compute first day of month n months ago ---
def _first_day_n_months_ago(ref_date: date, n: int) -> date:
    """Return the first day of the month that is n months before ref_date.
    n=1 -> first day of previous month; n=6 -> first day of month 6 months ago.
    """
    year = ref_date.year
    month = ref_date.month
    month -= n
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


def get_monthly_totals(
        db: Session, Model, converted_amount: Union[str, Any], date_field: str
):
    """
    Returns totals grouped by YYYY-MM for any model.
    converted_amount: either a SQL expression (case(...)) or string attribute name.
    date_field: str (earned_date / spent_date / investment_date)
    """
    col = _resolve_converted_column(Model, converted_amount)
    date_col = getattr(Model, date_field)

    dialect = _db_dialect_name(db)

    # Choose DB-specific month extractor / formatter
    if dialect in ("postgresql", "postgres"):
        month_expr = func.to_char(date_col, "YYYY-MM")
    elif dialect in ("mysql", "mariadb"):
        month_expr = func.date_format(date_col, "%Y-%m")
    else:
        # sqlite and fallback
        month_expr = func.strftime("%Y-%m", date_col)

    rows = (
        db.query(month_expr.label("month"), func.sum(col).label("total"))
        .group_by("month")
        .order_by("month")
        .all()
    )

    return [{"month": r.month, "total": float(r.total or 0)} for r in rows]


def get_spending_by_category(db: Session, ExpenseModel, converted_amount):
    """
    Returns total expense grouped by category NAME instead of category_id.
    """
    # Resolve column (SQL expression or ORM attribute)
    col = _resolve_converted_column(ExpenseModel, converted_amount)

    rows = (
        db.query(ExpenseCategory.name.label("category"), func.sum(col).label("total"))
        .join(
            ExpenseCategory,
            ExpenseModel.category_id == ExpenseCategory.expense_category_id,
        )
        .group_by(ExpenseCategory.name)
        .order_by(func.sum(col).desc())
        .all()
    )

    return [{"category": r.category, "amount": float(r.total or 0)} for r in rows]


class DashboardDataCalculator(BaseFetcher):
    def __init__(self):
        self.db: Session = next(get_db())
        self.cache_key_prefix = "dashboard"
        self.summary = "summary"
        self.cache_expiry_in_seconds = 86400

        super().__init__(
            "utilities.dashboard.calculator",
            self.cache_key_prefix,
            self.cache_expiry_in_seconds,
        )
        self.logger.debug("Dashboard calculator initialized")

    def get_converted_amount(
            self, model, amount_field, currency_field, is_currency_id=False
    ):
        """Helper to create currency conversion case statement.

        Creates a SQL CASE statement to convert amounts to INR based on currency.

        Args:
            model: SQLAlchemy model class
            amount_field: Name of the amount field to convert
            currency_field: Name of the currency field
            is_currency_id: Whether currency_field is an ID (True) or code (False)

        Returns:
            SQL CASE expression for converted amount in INR
        """
        """Helper to create currency conversion case statement."""
        # Fetch conversion rates once at the start
        conversion_rates = {
            "INR": self.get_conversion_rate_against_inr(currency_code="INR"),
            "USD": self.get_conversion_rate_against_inr(currency_code="USD"),
            "PLN": self.get_conversion_rate_against_inr(currency_code="PLN"),
        }

        # Currency ID to code mapping (if using currency_id)
        currency_id_map = {
            1: "INR",
            2: "USD",
            3: "PLN",
        }

        if is_currency_id:
            # For models using currency_id (integer)
            return case(
                *[
                    (
                        getattr(model, currency_field) == currency_id,
                        getattr(model, amount_field) * conversion_rates[currency_code],
                    )
                    for currency_id, currency_code in currency_id_map.items()
                ],
                else_=getattr(model, amount_field),
            )
        else:
            # For models using currency (string)
            return case(
                *[
                    (
                        getattr(model, currency_field) == currency_code,
                        getattr(model, amount_field) * rate,
                    )
                    for currency_code, rate in conversion_rates.items()
                ],
                else_=getattr(model, amount_field),
            )

    def get_investment_data(self) -> dict:
        """
        Extended full dashboard analytics including:
        - YTD & YoY income/expense/investment
        - Asset values and returns
        - Real cash balance (calculated)
        - Emergency fund coverage
        - Net worth
        - Savings rate
        - Category-wise spending
        - Monthly trends
        """

        # --- Try cache first ---
        cached_map = self.get_from_cache(self.cache_key_prefix, [self.summary])
        cached_info = cached_map.get(self.summary)
        if cached_info:
            self.logger.info("Cache hit :: Dashboard summary loaded from Redis Cache")
            return cached_info

        # ----- PORTFOLIO SUMMARY -----
        summary = get_portfolio_summary(self.db)
        total_cost = sum(v["total_cost"] for v in summary.values())
        total_current_value = sum(v["current_value"] for v in summary.values())
        total_returns = total_current_value - total_cost
        weighted_xirr = (
            sum(v["xirr"] * v["total_cost"] for v in summary.values()) / total_cost
            if total_cost
            else 0
        )

        def safe_get(key, field):
            return round(summary.get(key, {}).get(field, 0), 2)

        today = datetime.now().date()
        year_start = date(today.year, 1, 1)
        month_today = today.month

        # ---- LAST YEAR RANGE ----
        last_year_today = date(today.year - 1, month_today, today.day)
        last_year_start = date(today.year - 1, 1, 1)

        # ----- AMOUNTS CONVERTED -----
        income_converted_amount = self.get_converted_amount(
            Income, "amount", "currency"
        )
        expense_converted_amount = self.get_converted_amount(
            Expense, "amount", "currency"
        )
        stock_investment_converted_amount = self.get_converted_amount(
            StockInvestment, "total_invested_amount", "currency_id", is_currency_id=True
        )
        bullion_investment_converted_amount = self.get_converted_amount(
            BullionInvestment,
            "total_invested_amount",
            "currency_id",
            is_currency_id=True,
        )
        mutual_fund_converted_amount = self.get_converted_amount(
            MutualFundInvestment,
            "total_invested_amount",
            "currency_id",
            is_currency_id=True,
        )
        crypto_converted_amount = self.get_converted_amount(
            CryptoInvestment,
            "total_invested_amount",
            "currency_id",
            is_currency_id=True,
        )
        real_estate_converted_amount = self.get_converted_amount(
            RealEstateInvestment,
            "total_invested_amount",
            "currency_id",
            is_currency_id=True,
        )

        # ========== INCOME ==========
        income_ytd = get_ytd_sum(
            self.db, Income, income_converted_amount, "earned_date", year_start, today
        )
        income_last_year_to_date = get_last_year_sum(
            self.db,
            Income,
            income_converted_amount,
            "earned_date",
            last_year_start,
            last_year_today,
        )
        income_change = calculate_change(income_ytd, income_last_year_to_date)

        income = {
            "income": income_ytd,
            "income_last_year_to_date": income_last_year_to_date,
            "change": income_change,
        }

        # ========== EXPENSE ==========
        expense_ytd = get_ytd_sum(
            self.db, Expense, expense_converted_amount, "spent_date", year_start, today
        )
        expense_last_year_to_date = get_last_year_sum(
            self.db,
            Expense,
            expense_converted_amount,
            "spent_date",
            last_year_start,
            last_year_today,
        )
        monthly_avg_expense = expense_ytd / month_today if month_today > 0 else 0
        expense_change = calculate_change(expense_ytd, expense_last_year_to_date)
        expense_percentage_of_income = (
            (expense_ytd / income_ytd) * 100 if income_ytd > 0 else 0
        )

        expense = {
            "expense": expense_ytd,
            "expense_last_year_to_date": expense_last_year_to_date,
            "average_expense": monthly_avg_expense,
            "change": expense_change,
            "expense_ratio": expense_percentage_of_income,
        }

        # ========== INVESTMENT ==========
        # Sum all investment types for YTD
        investment_ytd = sum(
            [
                get_ytd_sum(
                    self.db,
                    StockInvestment,
                    stock_investment_converted_amount,
                    "investment_date",
                    year_start,
                    today,
                ),
                get_ytd_sum(
                    self.db,
                    BullionInvestment,
                    bullion_investment_converted_amount,
                    "investment_date",
                    year_start,
                    today,
                ),
                get_ytd_sum(
                    self.db,
                    MutualFundInvestment,
                    mutual_fund_converted_amount,
                    "investment_date",
                    year_start,
                    today,
                ),
                get_ytd_sum(
                    self.db,
                    CryptoInvestment,
                    crypto_converted_amount,
                    "investment_date",
                    year_start,
                    today,
                ),
                get_ytd_sum(
                    self.db,
                    RealEstateInvestment,
                    real_estate_converted_amount,
                    "investment_date",
                    year_start,
                    today,
                ),
            ]
        )

        # Sum all investment types for last year
        investment_last_year_to_date = sum(
            [
                get_last_year_sum(
                    self.db,
                    StockInvestment,
                    stock_investment_converted_amount,
                    "investment_date",
                    last_year_start,
                    last_year_today,
                ),
                get_last_year_sum(
                    self.db,
                    BullionInvestment,
                    bullion_investment_converted_amount,
                    "investment_date",
                    last_year_start,
                    last_year_today,
                ),
                get_last_year_sum(
                    self.db,
                    MutualFundInvestment,
                    mutual_fund_converted_amount,
                    "investment_date",
                    last_year_start,
                    last_year_today,
                ),
                get_last_year_sum(
                    self.db,
                    CryptoInvestment,
                    crypto_converted_amount,
                    "investment_date",
                    last_year_start,
                    last_year_today,
                ),
                get_last_year_sum(
                    self.db,
                    RealEstateInvestment,
                    real_estate_converted_amount,
                    "investment_date",
                    last_year_start,
                    last_year_today,
                ),
            ]
        )

        investment = {
            "investment": investment_ytd,
            "investment_last_year_to_date": investment_last_year_to_date,
            "average_investment": round(investment_ytd / month_today, 2),
            "investment_ratio": (
                investment_ytd / income_ytd * 100 if income_ytd else 0
            ),
            "change": calculate_change(investment_ytd, investment_last_year_to_date),
        }

        # ========== REAL CASH BALANCE (computed) ==========
        try:
            # use get_ytd_sum as a generic range-sum helper (start from a very early date)
            total_income_till_today = get_ytd_sum(
                self.db,
                Income,
                income_converted_amount,
                "earned_date",
                date(1970, 1, 1),
                today,
            )
        except Exception:
            total_income_till_today = 0

        try:
            total_expenses_till_today = get_ytd_sum(
                self.db,
                Expense,
                expense_converted_amount,
                "spent_date",
                date(1970, 1, 1),
                today,
            )
        except Exception:
            total_expenses_till_today = 0

        try:
            total_invested_till_today = (
                    get_ytd_sum(
                        self.db,
                        StockInvestment,
                        stock_investment_converted_amount,
                        "investment_date",
                        date(1970, 1, 1),
                        today,
                    )
                    + get_ytd_sum(
                self.db,
                BullionInvestment,
                bullion_investment_converted_amount,
                "investment_date",
                date(1970, 1, 1),
                today,
            )
                    + get_ytd_sum(
                self.db,
                MutualFundInvestment,
                mutual_fund_converted_amount,
                "investment_date",
                date(1970, 1, 1),
                today,
            )
                    + get_ytd_sum(
                self.db,
                CryptoInvestment,
                crypto_converted_amount,
                "investment_date",
                date(1970, 1, 1),
                today,
            )
                    + get_ytd_sum(
                self.db,
                RealEstateInvestment,
                real_estate_converted_amount,
                "investment_date",
                date(1970, 1, 1),
                today,
            )
            )
        except Exception:
            total_invested_till_today = 0

        cash_balance = (
                total_income_till_today
                - total_expenses_till_today
                - total_invested_till_today
        )

        # ========== EMERGENCY FUND ==========
        N = 6
        start_n_months_ago = _first_day_n_months_ago(today, N - 1)

        try:
            # We use your get_ytd_sum helper as a general range-sum: start_n_months_ago..today
            last_6_months_expense = get_ytd_sum(
                self.db,
                Expense,
                expense_converted_amount,
                "spent_date",
                start_n_months_ago,
                today,
            )
        except Exception:
            # fallback: approximate by monthly average * N (if available)
            try:
                monthly_avg = expense_ytd / (today.month if today.month else 1)
                last_6_months_expense = monthly_avg * N
            except Exception:
                last_6_months_expense = 0

        monthly_avg_6m = (last_6_months_expense / N) if N else 0
        emergency_required = monthly_avg_6m * 6
        emergency_coverage = (
            (cash_balance / emergency_required * 100) if emergency_required > 0 else 0
        )

        # ========== SAVINGS RATE ==========
        savings_ytd = income_ytd - expense_ytd
        savings_rate = (savings_ytd / income_ytd * 100) if income_ytd > 0 else 0

        # ========== NET WORTH ==========
        assets = {
            "Cash": round(cash_balance, 2),
            "Stocks": safe_get("stocks", "current_value"),
            "Mutual_Fund": safe_get("mutual_funds", "current_value"),
            "Gold": safe_get("gold", "current_value"),
            "Silver": safe_get("silver", "current_value"),
            "Land": safe_get("real_estate", "current_value"),
            "Crypto": safe_get("crypto", "current_value"),
        }
        net_worth = sum(assets.values())

        # ========== SPENDING CATEGORIES ==========
        spending_categories = get_spending_by_category(
            self.db, Expense, expense_converted_amount
        )

        # ========== MONTHLY TRENDS ==========
        monthly_trends = {
            "income": get_monthly_totals(
                self.db, Income, income_converted_amount, "earned_date"
            ),
            "expense": get_monthly_totals(
                self.db, Expense, expense_converted_amount, "spent_date"
            ),
        }

        # investment per-type and aggregated
        investment_models = [
            (
                "Stocks",
                StockInvestment,
                stock_investment_converted_amount,
                "investment_date",
            ),
            (
                "Bullion",
                BullionInvestment,
                bullion_investment_converted_amount,
                "investment_date",
            ),
            (
                "MutualFund",
                MutualFundInvestment,
                mutual_fund_converted_amount,
                "investment_date",
            ),
            ("Crypto", CryptoInvestment, crypto_converted_amount, "investment_date"),
            (
                "RealEstate",
                RealEstateInvestment,
                real_estate_converted_amount,
                "investment_date",
            ),
        ]

        investments_by_type = {}
        agg_map = defaultdict(float)

        for label, Model, conv_expr, date_field in investment_models:
            per_type = get_monthly_totals(self.db, Model, conv_expr, date_field)
            investments_by_type[label] = per_type
            for entry in per_type:
                m = entry.get("month")
                agg_map[m] += float(entry.get("total", 0.0))

        aggregated_investment = [
            {"month": m, "total": round(agg_map[m], 2)} for m in sorted(agg_map.keys())
        ]

        monthly_trends["investment"] = {
            "by_type": investments_by_type,
            "aggregated": aggregated_investment,
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
            "cash_balance": cash_balance,
            "emergency_coverage": round(emergency_coverage, 2),
            "income_ytd": income,
            "expense_avg": expense,
            "investment_avg": investment,
            "total_returns": round(total_returns, 2),
            "average_roi": round(weighted_xirr, 2),
            "savings_ytd": round(savings_ytd, 2),
            "savings_rate": round(savings_rate, 2),
            "assets": assets,
            "net_worth": round(net_worth, 2),
            "spending_categories": spending_categories,
            "investment_returns": investment_returns,
        }

        try:
            self.redis_client.setex(
                self.cache_key_prefix, self.cache_expiry_in_seconds, json.dumps(result)
            )
        except Exception as e:
            self.logger.warning(f"Cache write failed for {self.cache_key_prefix}: {e}")
            pass

        return result


# Global configuration instance
dashboardDataCalculator = DashboardDataCalculator()
