from sqlalchemy.orm import Session
from backend.schemas.investment_schemas import InvestmentCreate
from backend.summarizing import (
    update_stock_summary,
    update_mutual_fund_summary,
    update_crypto_summary,
    update_real_estate_summary,
    update_bullion_summary,
)

def update(investment_data: InvestmentCreate, db: Session):

    if investment_data.investment_subcategory_id is None:
        if investment_data.investment_type_id == 2:
            update_stock_summary.update(db, investment_data)
        elif investment_data.investment_type_id == 5:
            update_mutual_fund_summary.update(db, investment_data)
        elif investment_data.investment_type_id == 9:
            update_crypto_summary.update(db, investment_data)
    else:
        if investment_data.investment_type_id == 3:
            update_real_estate_summary.update(db, investment_data)
        elif investment_data.investment_type_id == 1:
            update_bullion_summary.update(db, investment_data)