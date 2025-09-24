import datetime

from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.crypto import CryptoSummary
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate


def update(db: Session, investment: CryptoInvestmentCreate):
    coin = db.query(CryptoSummary).filter(
        CryptoSummary.investor_id == investment.investor,
        CryptoSummary.coin_symbol == investment.coin_symbol,
        CryptoSummary.crypto_name == investment.crypto_name
    ).first()

    currency_map = {
        1: "INR",
        2: "PLN",
        3: "USD"
    }

    if coin:
        if investment.transaction_type == "BUY":
            coin.total_quantity += investment.coin_quantity
            coin.total_cost += investment.total_invested_amount
        elif investment.transaction_type == "SELL":
            coin.total_quantity -= investment.coin_quantity
            coin.total_cost -= (coin.average_price_per_unit * investment.coin_quantity)

            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=9,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today()  # type: ignore
            )
            db.add(income)

        coin.average_price_per_unit = coin.total_cost / coin.total_quantity if coin.total_quantity > 0 else 0
        coin.last_updated = datetime.datetime.utcnow()
    else:
        new_coin = CryptoSummary(
            investor_id=investment.investor,
            coin_symbol=investment.coin_symbol,
            crypto_name=investment.crypto_name,
            total_quantity=investment.coin_quantity,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount / investment.coin_quantity,
            last_updated=datetime.datetime.utcnow()
        )
        db.add(new_coin)

    db.commit()
