from fastapi import APIRouter, Query
from typing import Optional
from utilities.common.app_config import config

from backend.services.db_services import get_db
from sqlalchemy.orm import Session
from utilities.analytics.stock_analyzer import get_stock_score
from utilities.fetch_overall_investment_data import get_investments_symbols

logger = config.setup_logger("api.routes.analytics.score")
router = APIRouter(prefix="/analytics", tags=["analytics"])


# Get paginated and filtered stock scores for analytics
@router.get("/score")
async def get_stock_scores(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=500, description="Items per page"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    sub_sector: Optional[str] = Query(None, description="Filter by sub-sector"),
    search: Optional[str] = Query(None, description="Search by symbol"),
    filter_type: Optional[str] = Query(
        None, description="Filter by type: Core, Accelerator, GEM"
    ),
):
    """
    Get paginated stock scores with optional filtering.

    Args:
        page: Page number (1-indexed)
        limit: Number of items per page (max 500)
        sector: Filter by sector name
        sub_sector: Filter by sub-sector name
        search: Search by stock symbol (case-insensitive)
        filter_type: Filter by score type (Core > 0.2, Accelerator > 0.2, GEM > 0.2)

    Returns:
        {
            "data": [...],
            "page": 1,
            "limit": 100,
            "total": 500,
            "pages": 5,
            "has_more": true
        }
    """
    # Get all scores
    all_scores = get_stock_score()

    # Apply filters
    filtered_scores = all_scores

    if search:
        search_lower = search.lower()
        filtered_scores = [
            s for s in filtered_scores if search_lower in s.get("symbol", "").lower()
        ]

    if sector:
        filtered_scores = [s for s in filtered_scores if s.get("sector") == sector]

    if sub_sector:
        filtered_scores = [
            s for s in filtered_scores if s.get("sub_sector") == sub_sector
        ]

    if filter_type:
        if filter_type == "Core":
            filtered_scores = [s for s in filtered_scores if s.get("core", 0) > 0.2]
        elif filter_type == "Accelerator":
            filtered_scores = [
                s for s in filtered_scores if s.get("accelerators", 0) > 0.2
            ]
        elif filter_type == "GEM":
            filtered_scores = [s for s in filtered_scores if s.get("gem", 0) > 0.2]

    # Calculate pagination
    total = len(filtered_scores)
    pages = (total + limit - 1) // limit  # Ceiling division
    offset = (page - 1) * limit

    # Paginate
    paginated_scores = filtered_scores[offset : offset + limit]

    logger.info(
        f"Returning page {page}/{pages} with {len(paginated_scores)} stocks (total: {total})"
    )

    return {
        "data": paginated_scores,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "has_more": page < pages,
    }


# Get unique filter options (sectors, sub-sectors)
@router.get("/filters")
async def get_filter_options():
    """
    Get hierarchy of sectors and sub-sectors.

    Returns:
        {
            "sectors": {
                "Financials": ["Banks", "NBFCs", ...],
                "Technology": ["IT Services", "Software", ...]
            }
        }
    """
    all_scores = get_stock_score()

    # Build hierarchy: Sector -> Set of Sub-sectors
    sector_map = {}

    for s in all_scores:
        sec = s.get("sector")
        sub = s.get("sub_sector")

        if sec and sub:
            if sec not in sector_map:
                sector_map[sec] = set()
            sector_map[sec].add(sub)

    # Convert sets to sorted lists
    result = {k: sorted(list(v)) for k, v in sector_map.items()}

    return {"sectors": result}


# Get scores for currently invested stocks
@router.get("/invested_scores")
async def get_invested_stock_scores():
    """
    Get scores for stocks currently in the portfolio.
    If an invested stock is not found in the top 500 candidates (cached scores),
    it is returned with a 'Sell' recommendation.
    """
    db: Session = next(get_db())

    # Get invested symbols
    investment_data = get_investments_symbols(db)
    invested_symbols = set(
        investment_data.get("common_stocks", [])
        + investment_data.get("stocks_with_dividends", [])
    )

    # Filtering out ETFs etc if they are present in common_stocks (based on original screener logic)
    # The original logic filtered out: ["NIFTYBEES", "SILVERCASE", "MOMENTUM50"]
    # We should probably respect that or handle it.
    # But get_investments_symbols already separates these substantially.
    # Let's clean up just in case.
    excluded = {"NIFTYBEES", "SILVERCASE", "MOMENTUM50"}
    invested_symbols = {s for s in invested_symbols if s not in excluded}

    # Get all candidate scores
    all_scores = get_stock_score()
    score_map = {s.get("symbol"): s for s in all_scores}

    results = []

    for symbol in invested_symbols:
        stock_data = score_map.get(symbol)

        if stock_data:
            # Stock is in top 500, return as is (maybe add a flag? optional)
            results.append(stock_data)
        else:
            # Stock is NOT in top 500 -> Recommend Sell
            results.append(
                {
                    "symbol": symbol,
                    "recommendation": "Sell",
                    "reason": "Not in Top 500 candidates",
                    # Add dummy values for required fields to match StockData interface if strict,
                    # or rely on frontend to handle optional fields.
                    # Looking at frontend interface, fields are required.
                    # So we should provide safe defaults or make frontend interface optional.
                    # Let's provide safe defaults for now to avoid breaking current UI if it reuses components strictly.
                    "sector": "N/A",
                    "sub_sector": "N/A",
                    "core": 0,
                    "accelerators": 0,
                    "gem": 0,
                    "market_cap": 0,
                    "pe_ratio": 0,
                    "pb_ratio": 0,
                    "peg_ratio": 0,
                    "roe": 0,
                    "roce": 0,
                    "debt_to_equity": 0,
                    "promoter_holding": 0,
                    "ebitda_margin": 0,
                    "ev_ebitda": 0,
                }
            )

    return results
