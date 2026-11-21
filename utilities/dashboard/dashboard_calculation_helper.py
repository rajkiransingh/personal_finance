import json
from collections import defaultdict
from datetime import datetime, date, timedelta
from typing import Union, Any

from sqlalchemy import func, distinct
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import case

from backend.models.earnings.income import Income
from backend.models.investments.bullion import BullionInvestment
from backend.models.investments.crypto import CryptoInvestment
from backend.models.investments.mutual_fund import MutualFundInvestment
from backend.models.investments.real_estate import RealEstateInvestment
from backend.models.investments.stock import StockInvestment, Dividends
from backend.models.spendings.expense import Expense, ExpenseCategory, Liabilities, LiabilityValue
from backend.services.db_services import get_db
from utilities.common.base_fetcher import BaseFetcher, _build_cache_key
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


def get_dividend_history(db: Session, convert_to_inr):
    """Yearly dividend totals and the largest contributing stocks, in INR."""
    yearly = defaultdict(float)
    by_stock = defaultdict(float)
    id_to_code = {1: "INR", 2: "PLN", 3: "USD"}
    try:
        rows = db.query(
            Dividends.stock_symbol,
            Dividends.amount,
            Dividends.currency_id,
            Dividends.received_date,
        ).all()
        for symbol, amount, currency_id, received in rows:
            inr = float(amount or 0) * convert_to_inr(
                id_to_code.get(currency_id, "INR")
            )
            year = received.year if hasattr(received, "year") else str(received)[:4]
            yearly[str(year)] += inr
            by_stock[symbol or "Unknown"] += inr
    except Exception:
        pass

    years = [
        {"year": year, "amount": round(amount, 2)}
        for year, amount in sorted(yearly.items())
    ]
    stocks = [
        {"name": name, "amount": round(amount, 2)}
        for name, amount in sorted(by_stock.items(), key=lambda row: row[1], reverse=True)[:5]
    ]
    return years, stocks


def get_distinct_months(db: Session, Model, date_field: str, start: date, end: date) -> set:
    """Months (YYYY-MM) that actually contain at least one row in the given range."""
    date_col = getattr(Model, date_field)

    dialect = _db_dialect_name(db)
    if dialect in ("postgresql", "postgres"):
        month_expr = func.to_char(date_col, "YYYY-MM")
    elif dialect in ("mysql", "mariadb"):
        month_expr = func.date_format(date_col, "%Y-%m")
    else:
        month_expr = func.strftime("%Y-%m", date_col)

    rows = (
        db.query(distinct(month_expr))
        .filter(date_col >= start, date_col <= end)
        .all()
    )
    return {row[0] for row in rows if row[0]}


def get_liability_totals(db: Session, today: date, convert_to_inr):
    """Latest value per individual loan, converted to INR. One loan = type + comment."""
    try:
        rows = (
            db.query(
                LiabilityValue.liability_id,
                LiabilityValue.comment,
                LiabilityValue.value,
                LiabilityValue.currency,
                LiabilityValue.date,
            )
            .filter(LiabilityValue.date <= today)
            .order_by(
                LiabilityValue.liability_id,
                LiabilityValue.comment,
                LiabilityValue.date.desc(),
            )
            .all()
        )
        latest = {}
        for liability_id, comment, value, currency, _ in rows:
            key = (liability_id, comment or "")
            if key not in latest:
                rate = convert_to_inr(currency or "INR")
                latest[key] = float(value or 0) * rate

        names = {
            row.liability_id: row.liability_type
            for row in db.query(Liabilities).all()
        }
        breakdown = []
        for (liability_id, comment), value in latest.items():
            label = names.get(liability_id, f"Liability {liability_id}")
            if comment:
                label = f"{label} · {comment}"
            breakdown.append({"name": label, "value": round(value, 2)})
        breakdown.sort(key=lambda entry: entry["value"], reverse=True)
        return round(sum(latest.values()), 2), breakdown
    except Exception:
        return 0.0, []


def get_spending_by_category(
    db: Session, ExpenseModel, converted_amount, start: date = None, end: date = None
):
    """Expense totals by category name, optionally limited to a date range."""
    col = _resolve_converted_column(ExpenseModel, converted_amount)
    query = db.query(
        ExpenseCategory.name.label("category"), func.sum(col).label("total")
    ).join(
        ExpenseCategory,
        ExpenseModel.category_id == ExpenseCategory.expense_category_id,
    )
    if start is not None:
        query = query.filter(ExpenseModel.spent_date >= start)
    if end is not None:
        query = query.filter(ExpenseModel.spent_date <= end)

    rows = query.group_by(ExpenseCategory.name).order_by(func.sum(col).desc()).all()

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
            2: "PLN",
            3: "USD",
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

    def get_investment_data(self, force_refresh: bool = False) -> dict:
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

        # --- Try cache first (unless force_refresh is requested) ---
        if not force_refresh:
            cached_map = self.get_from_cache(self.cache_key_prefix, [self.summary])
            cached_info = cached_map.get(self.summary)
            if cached_info:
                return cached_info

        # This calculator is a long-lived singleton. Close any open transaction
        # so the next queries see rows added since the previous calculation.
        self.db.rollback()

        # ----- PORTFOLIO SUMMARY -----
        summary = get_portfolio_summary(self.db)
        total_cost = sum(v["total_cost"] for v in summary.values())
        total_current_value = sum(v["current_value"] for v in summary.values())
        total_returns = total_current_value - total_cost
        total_return_pct = (total_returns / total_cost * 100) if total_cost else 0
        weighted_xirr = (
            sum(v["xirr"] * v["total_cost"] for v in summary.values()) / total_cost
            if total_cost
            else 0
        )

        # Per-class detail so the dashboard can show absolute gains alongside XIRR.
        investment_breakdown = []
        for key, label in (
            ("stocks", "Stocks"),
            ("mutual_funds", "Mutual funds"),
            ("gold", "Gold"),
            ("silver", "Silver"),
            ("real_estate", "Real estate"),
            ("crypto", "Crypto"),
        ):
            entry = summary.get(key, {})
            cost = entry.get("total_cost", 0)
            current = entry.get("current_value", 0)
            investment_breakdown.append(
                {
                    "name": label,
                    "total_cost": round(cost, 2),
                    "current_value": round(current, 2),
                    "gain": round(current - cost, 2),
                    "xirr": round(entry.get("xirr", 0), 2),
                }
            )
        investment_breakdown.sort(key=lambda row: row["gain"], reverse=True)

        def safe_get(key, field):
            return round(summary.get(key, {}).get(field, 0), 2)

        today = datetime.now().date()
        year_start = date(today.year, 1, 1)
        month_today = today.month

        # ---- LAST YEAR RANGE ----
        try:
            last_year_today = date(today.year - 1, month_today, today.day)
        except ValueError:
            # 29 February has no counterpart in a non-leap year.
            last_year_today = date(today.year - 1, month_today, 28)
        last_year_start = date(today.year - 1, 1, 1)

        # ---- DATA COVERAGE ----
        # Averages are divided by months that actually contain rows, not by the
        # calendar month number. Otherwise a quiet November drags every average down.
        income_months = get_distinct_months(
            self.db, Income, "earned_date", year_start, today
        )
        expense_months = get_distinct_months(
            self.db, Expense, "spent_date", year_start, today
        )
        investment_months = set()
        for Model, date_field in (
            (StockInvestment, "investment_date"),
            (BullionInvestment, "investment_date"),
            (MutualFundInvestment, "investment_date"),
            (CryptoInvestment, "investment_date"),
            (RealEstateInvestment, "investment_date"),
        ):
            investment_months |= get_distinct_months(
                self.db, Model, date_field, year_start, today
            )

        active_income_months = len(income_months) or 1
        active_expense_months = len(expense_months) or 1
        active_investment_months = len(investment_months) or 1

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
            "average_income": round(income_ytd / active_income_months, 2),
            "active_months": len(income_months),
            "last_month": max(income_months) if income_months else None,
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
        monthly_avg_expense = expense_ytd / active_expense_months
        expense_change = calculate_change(expense_ytd, expense_last_year_to_date)
        expense_percentage_of_income = (
            (expense_ytd / income_ytd) * 100 if income_ytd > 0 else 0
        )

        expense = {
            "expense": expense_ytd,
            "expense_last_year_to_date": expense_last_year_to_date,
            "average_expense": round(monthly_avg_expense, 2),
            "active_months": len(expense_months),
            "last_month": max(expense_months) if expense_months else None,
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

        try:
            active_sip_count = int(
                self.db.query(func.count(distinct(MutualFundInvestment.scheme_code)))
                .filter(
                    MutualFundInvestment.investment_date >= year_start,
                    MutualFundInvestment.investment_date <= today,
                    MutualFundInvestment.transaction_type == "BUY",
                )
                .scalar()
                or 0
            )
        except Exception:
            active_sip_count = 0

        investment = {
            "investment": investment_ytd,
            "investment_last_year_to_date": investment_last_year_to_date,
            "average_investment": round(investment_ytd / active_investment_months, 2),
            "active_months": len(investment_months),
            "last_month": max(investment_months) if investment_months else None,
            "active_sip_count": active_sip_count,
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
        # Target: six months of the average monthly expense, measured across the
        # last six COMPLETE calendar months. The current (partial) month is
        # excluded so an empty or half-finished month cannot dilute the average.
        EMERGENCY_MONTHS = 6
        window_start = _first_day_n_months_ago(today, EMERGENCY_MONTHS)
        window_end = date(today.year, today.month, 1) - timedelta(days=1)

        try:
            last_6_months_expense = get_ytd_sum(
                self.db,
                Expense,
                expense_converted_amount,
                "spent_date",
                window_start,
                window_end,
            )
        except Exception as e:
            self.logger.warning(
                f"Emergency fund expense window failed: {e}; falling back to YTD monthly average"
            )
            last_6_months_expense = monthly_avg_expense * EMERGENCY_MONTHS

        monthly_avg_6m = last_6_months_expense / EMERGENCY_MONTHS
        emergency_required = monthly_avg_6m * EMERGENCY_MONTHS
        emergency_coverage = (
            (cash_balance / emergency_required * 100) if emergency_required > 0 else 0
        )

        # ========== NEXT-MONTH FORECAST ==========
        # Based on the same active-month averages used by the KPI cards, not a
        # bill schedule. The UI states this explicitly.
        forecast = {
            "inflow": round(income["average_income"], 2),
            "outflow": round(expense["average_expense"], 2),
            "net_savings": round(
                income["average_income"] - expense["average_expense"], 2
            ),
        }

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
        total_assets = sum(assets.values())
        total_liabilities, liability_breakdown = get_liability_totals(
            self.db, today, self.get_conversion_rate_against_inr
        )
        net_worth = total_assets - total_liabilities

        # ========== SPENDING CATEGORIES ==========
        spending_categories = get_spending_by_category(
            self.db, Expense, expense_converted_amount, year_start, today
        )
        dividend_yearly, dividend_top_stocks = get_dividend_history(
            self.db, self.get_conversion_rate_against_inr
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
            "emergency_fund_required": round(emergency_required, 2),
            "emergency_monthly_average": round(monthly_avg_6m, 2),
            "total_invested_cost": round(total_cost, 2),
            "income_ytd": income,
            "expense_avg": expense,
            "investment_avg": investment,
            "total_returns": round(total_returns, 2),
            "total_return_pct": round(total_return_pct, 2),
            "invested_current_value": round(total_current_value, 2),
            "investment_breakdown": investment_breakdown,
            "average_roi": round(weighted_xirr, 2),
            "savings_ytd": round(savings_ytd, 2),
            "savings_rate": round(savings_rate, 2),
            "forecast": forecast,
            "assets": assets,
            "total_assets": round(total_assets, 2),
            "total_liabilities": total_liabilities,
            "liability_breakdown": liability_breakdown,
            "net_worth": round(net_worth, 2),
            "spending_categories": spending_categories,
            "dividend_yearly": dividend_yearly,
            "dividend_top_stocks": dividend_top_stocks,
            "investment_returns": investment_returns,
        }

        try:
            self.redis_client.setex(
                _build_cache_key(self.cache_key_prefix, self.summary),
                self.cache_expiry_in_seconds,
                json.dumps(result),
            )
        except Exception as e:
            self.logger.warning(f"Cache write failed for {self.cache_key_prefix}: {e}")
            pass

        return result


# Global configuration instance
dashboardDataCalculator = DashboardDataCalculator()
