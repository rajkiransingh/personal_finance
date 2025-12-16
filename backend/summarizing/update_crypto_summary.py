import datetime

import redis
from datetime import date
from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.crypto import CryptoSummary
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate


def update(db: Session, investment: CryptoInvestmentCreate):
    currency_map = {
        1: "INR",
        2: "PLN",
        3: "USD"
    }

    # Initialize Redis
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    redis_forex_key_usd_inr = redis_client.get("forex::USD:INR")
    redis_forex_key_pln_inr = redis_client.get("forex::PLN:INR")

    # Calculate cost in INR
    invested_currency = currency_map.get(investment.currency_id, "INR")

    if invested_currency == "INR":
        conversion_rate = 1.0
    elif invested_currency == "PLN":
        conversion_rate = round(float(redis_forex_key_pln_inr), 2)
    elif invested_currency == "USD":
        conversion_rate = round(float(redis_forex_key_usd_inr), 2)
    else:
        raise Exception(f"Unsupported currency type: {invested_currency}")

    coin = db.query(CryptoSummary).filter(
        CryptoSummary.investor_id == investment.investor,
        CryptoSummary.coin_symbol == investment.coin_symbol,
        CryptoSummary.crypto_name == investment.crypto_name
    ).first()

    if coin:
        if investment.transaction_type == "BUY":
            coin.total_quantity += investment.coin_quantity
            coin.total_cost += investment.total_invested_amount * conversion_rate
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
        # Adding new coin
        new_coin = CryptoSummary(
            investor_id=investment.investor,
            coin_symbol=investment.coin_symbol,
            crypto_name=investment.crypto_name,
            total_quantity=investment.coin_quantity,
            total_cost=investment.total_invested_amount * conversion_rate,
            average_price_per_unit=investment.total_invested_amount / investment.coin_quantity,
            last_updated=datetime.datetime.utcnow()
        )
        db.add(new_coin)

    db.commit()
