from sqlalchemy.orm import Session
from backend.models import models

def update(db: Session, investment: models.Dividends):
    dividend = db.query(models.DividentSummary).filter(
        models.DividentSummary.investor == investment.investor,
        models.DividentSummary.stock_symbol == investment.stock_symbol
    ).first()

    currency_map = {
        1: "INR",
        2: "PLN",
        3: "USD"
    }

    if dividend:
        dividend.total_amount += investment.amount
          
        income = models.Income(
            user_id=investment.investor,
            source_id=4,
            amount=investment.amount,
            currency=currency_map[investment.currency_id],
            earned_date=investment.received_date or date.today() # type: ignore
        )
        db.add(income)

    else:
        new_stock = models.DividentSummary(
            investor=investment.investor,
            currency_id=investment.currency_id,
            region_id=investment.region_id,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_amount=investment.amount,
        )
        db.add(new_stock)

    db.commit()