from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionSummary
from backend.models.investments.crypto import CryptoSummary
from backend.models.investments.mutual_fund import MutualFundSummary
from backend.models.investments.real_estate import RealEstateSummary
from backend.models.investments.stock import StockSummary, DividendSummary


def get_investments_symbols(db: Session):
    """Return categorized lists of investment symbols."""
    stocks = db.query(StockSummary).all()

    return {
        "common_stocks": [s.stock_symbol for s in stocks if not s.dividend_paying],
        "stocks_with_dividends": [s.stock_symbol for s in stocks if s.dividend_paying],
        "mutual_funds": [m.scheme_code for m in db.query(MutualFundSummary).all()],
        "crypto": [c.coin_symbol for c in db.query(CryptoSummary).all()],
        "bullion": sorted({b.metal_name for b in db.query(BullionSummary).all()}),
    }


def get_all_investments(db: Session):
    """Fetch all investment summaries by type."""
    models = {
        "stocks": StockSummary,
        "mutual_funds": MutualFundSummary,
        "bullion": BullionSummary,
        "real_estate": RealEstateSummary,
        "crypto": CryptoSummary,
    }
    return {name: db.query(model).all() for name, model in models.items()}


def get_portfolio_summary(db: Session):
    """
        Aggregate portfolio totals and weighted XIRR across all asset types.
        Bullion is grouped per metal_name; others are summed.
        """

    models = {
        'stocks': StockSummary,
        'mutual_funds': MutualFundSummary,
        'bullion': BullionSummary,
        'real_estate': RealEstateSummary,
        'crypto': CryptoSummary
    }

    summary = {}
    for name, model in models.items():
        if name == "bullion":
            # Query per metal_name instead of one sum
            query = select(
                model.metal_name,
                func.sum(model.total_cost).label('total_cost'),
                func.sum(model.current_value).label('current_value'),
                (func.sum(model.xirr * model.total_cost) / func.sum(model.total_cost)).label('xirr')
            ).group_by(model.metal_name)

            results = db.execute(query).all()

            for r in results:
                metal_name = r.metal_name.lower()
                summary[metal_name] = {
                    "total_cost": float(r.total_cost or 0),
                    "current_value": float(r.current_value or 0),
                    "xirr": round(float(r.xirr or 0), 2),
                }

        else:
            result = db.execute(
                select(
                    func.sum(model.total_cost).label("total_cost"),
                    func.sum(model.current_value).label("current_value"),
                    (
                            func.sum(model.xirr * model.total_cost) / func.nullif(func.sum(model.total_cost), 0)
                    ).label("xirr"),
                )
            ).first()

            summary[name] = {
                "total_cost": float(result.total_cost or 0),
                "current_value": float(result.current_value or 0),
                "xirr": round(float(result.xirr or 0), 2),
            }

    return summary


def get_investments_with_sub_allocations(db: Session):
    """Return detailed investment breakdown (stocks categorized by type)."""
    investments = get_all_investments(db)

    detailed_data = {
        "etf": [],
        "reits": [],
        "stock": [],
        "mutual_funds": investments.get("mutual_funds", []),
        "bullion": investments.get("bullion", []),
        "real_estate": investments.get("real_estate", []),
        "crypto": investments.get("crypto", []),
    }

    for inv in investments.get("stocks", []):
        detailed_data[categorize_stock(inv.stock_symbol)].append(inv)

    return detailed_data


def categorize_stock(symbol: str) -> str:
    """Classify stock symbol into ETF, REIT, bullion ETF, or normal stock."""
    s = symbol.upper()

    if any(k in s for k in ["GOLD", "SILVER"]):
        return "bullion"
    if any(k in s for k in ["-RR", "REIT", "INVIT"]):
        return "reits"
    if any(k in s for k in ["BEES", "ETF", "CASE", "MOMENTUM50"]):
        return "etf"

    return "stock"


def get_dividends_data(db: Session):
    """Return dict mapping stock symbols to their total dividend amount."""
    return dict(db.query(DividendSummary.stock_symbol, DividendSummary.total_amount))
