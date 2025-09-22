from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.models import StockInvestment, MutualFundInvestment, BullionInvestment, RealEstateInvestment, CryptoInvestment
from backend.schemas.investment_schemas import StockInvestmentResponse, MutualFundInvestmentResponse, BullionInvestmentResponse, RealEstateInvestmentResponse, CryptoInvestmentResponse, InvestmentUpdate
from datetime import date

def get_all_investments(type: str, db: Session):
    if type == "stock":
        return db.query(StockInvestment).all()
    elif type == "mutual fund":
        return db.query(MutualFundInvestment).all()
    elif type == "bullion":
        return db.query(BullionInvestment).all()
    elif type == "real estate":
        return db.query(RealEstateInvestment).all()
    elif type == "crypto":
        return db.query(CryptoInvestment).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

def get_investment_by_user(type :str, db: Session, user_id: int):
    if type == "stock":
        return db.query(StockInvestment).filter(StockInvestment.investor == user_id).all()
    elif type == "mutual fund":
        return db.query(MutualFundInvestment).filter(MutualFundInvestment.investor == user_id).all()
    elif type == "bullion":
        return db.query(BullionInvestment).filter(BullionInvestment.investor == user_id).all()
    elif type == "real estate":
        return db.query(RealEstateInvestment).filter(RealEstateInvestment.investor == user_id).all()
    elif type == "crypto":
        return db.query(CryptoInvestment).filter(CryptoInvestment.investor == user_id).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")
    
def get_investment_by_id(type :str, db: Session, id: int):
    if type == "stock":
        return db.query(StockInvestment).filter(StockInvestment.id == id).first()
    elif type == "mutual fund":
        return db.query(MutualFundInvestment).filter(MutualFundInvestment.id == id).first()
    elif type == "bullion":
        return db.query(BullionInvestment).filter(BullionInvestment.id == id).first()
    elif type == "real estate":
        return db.query(RealEstateInvestment).filter(RealEstateInvestment.id == id).first()
    elif type == "crypto":
        return db.query(CryptoInvestment).filter(CryptoInvestment.id == id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

def create_stock(stock_data: StockInvestmentResponse, db: Session):
    if stock_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if stock_data.transaction_type == "SELL":
        total_holdings = db.query(StockInvestment).filter(
            StockInvestment.investor == stock_data.investor,
            StockInvestment.stock_symbol == stock_data.stock_symbol
        ).all()

        total_quantity = sum(holding.stock_quantity for holding in total_holdings)

        if stock_data.stock_quantity > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = StockInvestment(
        investor=stock_data.investor,
        currency_id=stock_data.currency_id,
        investment_type_id=stock_data.investment_type_id,
        investment_subcategory_id=stock_data.investment_subcategory_id,
        transaction_type=stock_data.transaction_type,
        stock_symbol=stock_data.stock_symbol,
        stock_name=stock_data.stock_name,
        initial_price_per_stock=stock_data.initial_price_per_stock,
        stock_quantity=stock_data.stock_quantity,
        total_invested_amount=stock_data.total_invested_amount,
        total_amount_after_sale=stock_data.total_amount_after_sale,
        investment_date=stock_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def create_mutual_fund(fund_data: MutualFundInvestmentResponse, db: Session):
    if fund_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if fund_data.transaction_type == "SELL":
        total_holdings = db.query(MutualFundInvestment).filter(
            MutualFundInvestment.investor == fund_data.investor,
            MutualFundInvestment.scheme_code == fund_data.scheme_code
        ).all()

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
        total_amount_after_sale = fund_data.total_amount_after_sale,
        investment_date=fund_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def create_bullion(bullion_data: BullionInvestmentResponse, db: Session):
    if bullion_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if bullion_data.transaction_type == "SELL":
        total_holdings = db.query(BullionInvestment).filter(
            BullionInvestment.investor == bullion_data.investor,
            BullionInvestment.metal_name == bullion_data.metal_name,
            BullionInvestment.investment_subcategory_id == bullion_data.investment_subcategory_id
        ).all()

        total_quantity = sum(holding.quantity_in_grams for holding in total_holdings)

        if bullion_data.quantity_in_grams > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = BullionInvestment(
        investor=bullion_data.investor,
        currency_id=bullion_data.currency_id,
        investment_type_id=bullion_data.investment_type_id,
        investment_subcategory_id=bullion_data.investment_subcategory_id,
        transaction_type=bullion_data.transaction_type,
        metal_name=bullion_data.metal_name,
        initial_price_per_gram=bullion_data.initial_price_per_gram,
        quantity_in_grams=bullion_data.quantity_in_grams,
        total_invested_amount=bullion_data.total_invested_amount,
        total_amount_after_sale = bullion_data.total_amount_after_sale,
        investment_date=bullion_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def create_property(property_data: RealEstateInvestmentResponse, db: Session):
    if property_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if property_data.transaction_type == "SELL":
        total_holdings = db.query(RealEstateInvestment).filter(
            RealEstateInvestment.investor == property_data.investor,
            RealEstateInvestment.property_type == property_data.property_type,
            RealEstateInvestment.property_location == property_data.property_location,
            RealEstateInvestment.investment_subcategory_id == property_data.investment_subcategory_id
        ).all()

        total_quantity = sum(holding.area_in_sqyds for holding in total_holdings)

        if property_data.area_in_sqyds > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = RealEstateInvestment(
        investor=property_data.investor,
        currency_id=property_data.currency_id,
        investment_type_id=property_data.investment_type_id,
        investment_subcategory_id=property_data.investment_subcategory_id,
        transaction_type=property_data.transaction_type,
        property_name=property_data.property_name,
        property_type=property_data.property_type,
        property_location=property_data.property_location,
        initial_price_per_sqyds=property_data.initial_price_per_sqyds,
        area_in_sqyds=property_data.area_in_sqyds,
        total_invested_amount=property_data.total_invested_amount,
        total_amount_after_sale = property_data.total_amount_after_sale,
        investment_date=property_data.investment_date or date.today()
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def create_crypto(coin_data: CryptoInvestmentResponse, db: Session):
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
        total_amount_after_sale = coin_data.total_amount_after_sale,
        investment_date=coin_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

def update_investment(type: str, id: int, update_data: InvestmentUpdate, db: Session):
    """
    Updates only the provided fields for the investment transaction while keeping other values unchanged.
    """
    if (type == "stock"):
        investment = db.query(StockInvestment).filter(StockInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "mutual fund"):
        investment = db.query(MutualFundInvestment).filter(MutualFundInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "bullion"):
        investment = db.query(BullionInvestment).filter(BullionInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "real estate"):
        investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "crypto"):
        investment = db.query(CryptoInvestment).filter(CryptoInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

    # Apply updates only if the field is provided
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(investment, key, value)

    db.commit()
    db.refresh(investment)

    return investment

def delete_investment(type: str, id: int, db: Session):
    if (type == "stock"):
        investment = db.query(StockInvestment).filter(StockInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "mutual fund"):
        investment = db.query(MutualFundInvestment).filter(MutualFundInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "bullion"):
        investment = db.query(BullionInvestment).filter(BullionInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "real estate"):
        investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif (type == "crypto"):
        investment = db.query(CryptoInvestment).filter(CryptoInvestment.id == id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")
    
    db.delete(investment)
    db.commit()
    return investment