from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.mutual_fund import MutualFundInvestment
from backend.schemas.investments.mutual_fund_schema import MutualFundInvestmentCreate


def create_mutual_fund(db: Session, fund_data: MutualFundInvestmentCreate):
    if fund_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if fund_data.transaction_type == "SELL":
        total_holdings = (
            db.query(MutualFundInvestment)
            .filter(
                MutualFundInvestment.investor == fund_data.investor,
                MutualFundInvestment.scheme_code == fund_data.scheme_code,
            )
            .all()
        )

        total_quantity = sum(holding.unit_quantity for holding in total_holdings)

        if fund_data.unit_quantity > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = MutualFundInvestment(
        investor=fund_data.investor,
        currency_id=fund_data.currency_id,
        investment_type_id=fund_data.investment_type_id,
        investment_subcategory_id=fund_data.investment_subcategory_id,
        transaction_type=fund_data.transaction_type,
        scheme_code=fund_data.scheme_code,
        fund_name=fund_data.fund_name,
        initial_price_per_unit=fund_data.initial_price_per_unit,
        unit_quantity=fund_data.unit_quantity,
        total_invested_amount=fund_data.total_invested_amount,
        total_amount_after_sale=fund_data.total_amount_after_sale,
        investment_date=fund_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
