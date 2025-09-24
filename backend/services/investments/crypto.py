from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.crypto import CryptoInvestment
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate


def create_crypto(db: Session, coin_data: CryptoInvestmentCreate):
    if coin_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if coin_data.transaction_type == "SELL":
        total_holdings = db.query(CryptoInvestment).filter(
            CryptoInvestment.investor == coin_data.investor,
            CryptoInvestment.coin_symbol == coin_data.coin_symbol,
            CryptoInvestment.investment_type_id == coin_data.investment_type_id
        ).all()

        total_quantity = sum(holding.coin_quantity for holding in total_holdings)

        if coin_data.coin_quantity > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = CryptoInvestment(
        investor=coin_data.investor,
        currency_id=coin_data.currency_id,
        investment_type_id=coin_data.investment_type_id,
        investment_subcategory_id=coin_data.investment_subcategory_id,
        transaction_type=coin_data.transaction_type,
        coin_symbol=coin_data.coin_symbol,
        crypto_name=coin_data.crypto_name,
        initial_price_per_coin=coin_data.initial_price_per_coin,
        coin_quantity=coin_data.coin_quantity,
        total_invested_amount=coin_data.total_invested_amount,
        total_amount_after_sale=coin_data.total_amount_after_sale,
        investment_date=coin_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
