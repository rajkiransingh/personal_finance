from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.models.models import StockInvestment, MutualFundInvestment, StockSummary, MutualFundSummary, CryptoSummary, BullionSummary, Dividends, DividendSummary
from utilities.get_exchange_rates import get_exchange_rates
from utilities.get_mf_rates import get_mutual_fund_rates_bulk, get_mutual_fund_nav_dict
from utilities.get_current_metal_rates import get_current_metal_rates
from utilities.get_stock_prices import get_stock_prices_in_bulk
from backend.services.db_services import get_db
import json
import logging
from datetime import datetime
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Investment_updater_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("investment_summary_updater")

def main():
    logger.info("Starting investment update job")
    
    try:
        # Get database session
        db = next(get_db())

        # Get all investment data and stock prices upfront
        all_investment_data_summary = get_data_from_investment_summary(db)

        # Get All the dividends data
        dividends_data = get_dividends_data(db)
        
        # Extracting investment specific data from the DB
        common_stock_list = all_investment_data_summary.get("common_stocks", {})
        dividend_stock_list = all_investment_data_summary.get("stocks_with_dividends", {})
        mutual_funds_list = all_investment_data_summary['mutual_funds']
        
        # Get the latest prices and NAVs
        logger.info(f"Common Stock Summary List: {common_stock_list}")
        logger.info(f"Dividend Stock Summary List: {dividend_stock_list}")
        logger.info(f"Mutual Fund Summary List: {mutual_funds_list}")
        
        common_stock_prices = get_stock_prices_in_bulk(common_stock_list)
        dividend_stock_prices = get_stock_prices_in_bulk(dividend_stock_list)

        logger.info(f"Mutual Fund list: {mutual_funds_list}")
        All_mutual_fund_data = get_mutual_fund_rates_bulk(mutual_funds_list)
        mf_navs = get_mutual_fund_nav_dict(All_mutual_fund_data)
        logger.info(f"MF NAVs: {mf_navs}")
        
        # Update database with latest values
        logger.info("Updating common stock investments")
        update_stock_prices(db, common_stock_prices, dividend_stock_prices, dividends_data)
        
        logger.info("Updating mutual fund investments")
        update_mutual_fund_values(db, mf_navs)
        
        logger.info("Investment update job completed successfully")
    
    except Exception as e:
        logger.error(f"Investment update job failed: {str(e)}")
        sys.exit(1)
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()

def update_stock_prices(db, common_stock_prices, dividend_stock_prices, dividends_data):
    """
    Updates StockInvestment records with latest prices and calculates derived values.
    
    Args:
        db: Database session object
    
    Returns:
        int: Number of successfully updated stock investments
    
    Raises:
        Exception: If there's an error during the update process
    """
    try:        
        # Get all stock investments in a single query
        stock_investments = db.query(StockInvestment).all()
        
        updated_count = 0
        current_price = 0
        today = datetime.now().date()
        
        for investment in stock_investments:
            # Get the specific stock price data for this investment
            stock_price_data = dividend_stock_prices.get(investment.stock_symbol) if investment.dividend_paying == 1 else common_stock_prices.get(investment.stock_symbol)
            
            dividend_amount = dividends_data.get(investment.stock_symbol, 0)
            logger.info(f"Found total dividends received for {investment.stock_symbol} is: {dividend_amount}")

            # Skip if no price data available for this stock
            if not stock_price_data:
                logger.warning(f"No price data available for {investment.stock_symbol}")
                continue
            # Extract the current price from the price data

            if isinstance(stock_price_data, str):
                 json_data = json.loads(stock_price_data)
                 current_price = json_data["currentPrice"]

            # Assuming the price is stored under a specific key or is the value itself
            if isinstance(stock_price_data, dict) and "currentPrice" in stock_price_data:
                current_price = stock_price_data["currentPrice"]
                if current_price == 'N/A':
                    logger.warning(f"Unable to fetch the price for {investment.stock_symbol}, switching to previous closed price")
                    current_price = stock_price_data["previousClose"]
            
            # Validate price data
            if not is_valid_price(current_price):
                logger.warning(f"Skipping {investment.stock_symbol} - Invalid price: {current_price}")
                continue
            
            # Convert to float if it's a numeric string
            if isinstance(current_price, str):
                current_price = float(current_price)
            
            # Update investment with new calculations
            update_investment_calculations(investment, current_price, dividend_amount, today)
            updated_count += 1
            
            logger.info(
                f"Updated {investment.stock_symbol} - "
                f"Current Price: {current_price}, "
                f"Total Value: {investment.current_total_value}, "
                f"ROI: {investment.return_on_investment:.2f}%, "
                f"XIRR: {investment.xirr:.2f}%"
            )
        
        # Commit all changes to the database
        db.commit()
        logger.info(f"Updated {updated_count} stock investments")
        return updated_count
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stock prices: {str(e)}")
        raise

def is_valid_price(price):
    """
    Validates if a price value is usable for calculations.
    
    Args:
        price: The price value to validate
        
    Returns:
        bool: True if the price is valid, False otherwise
    """
    if price == "N/A":
        return False
    
    if isinstance(price, str) and not price.replace('.', '', 1).isdigit():
        return False
        
    return True

def update_investment_calculations(investment, current_price, dividend_amount, today):
    """
    Updates an investment with calculated values based on current price.
    
    Args:
        investment: The StockInvestment object to update
        current_price: The current price of the stock
        today: Current date for calculating investment duration
    """
    # Update current price
    investment.current_price_per_stock = current_price
    
    # Calculate current total value
    investment.current_total_value = float(current_price) * float(investment.stock_quantity)
    
    # Calculate return on investment (ROI) as percentage
    initial_investment = investment.total_invested_amount
    current_value = investment.current_total_value

    logger.info(f"Using the received Dividends amount in the roi and xirr calculation: {dividend_amount}")
    investment.return_on_investment = (((current_value + dividend_amount) - initial_investment) / initial_investment) * 100
    
    # Calculate XIRR (simplified version)
    days_invested = (today - investment.investment_date).days
    years = days_invested / 365.0
    
    investment.xirr = ((((current_value + dividend_amount) / initial_investment) ** (1 / years)) - 1) * 100 if years > 0 else 0.0


def update_mutual_fund_values(db, mf_navs):
    """
    Updates MutualFundInvestment records with latest NAVs and calculates derived values
    """
    updated_count = 0
    try:
        # Get all mutual fund investments
        mf_investments = db.query(MutualFundInvestment).all()
        
        for investment in mf_investments:
            # Assuming scheme_code is the field name - adjust if different
            scheme_code = investment.scheme_code
            
            if scheme_code in mf_navs:
                current_nav = mf_navs[scheme_code]
                
                # Skip if NAV is not available
                if current_nav == "N/A" or isinstance(current_nav, str) and not current_nav.replace('.', '', 1).isdigit():
                    logger.warning(f"Skipping {scheme_code} - Invalid NAV: {current_nav}")
                    continue
                
                # Convert string to float if necessary
                if isinstance(current_nav, str):
                    current_nav = float(current_nav)
                    
                # Update current NAV and related fields
                logger.info(f"Got the total quantity: {investment.unit_quantity} and current price: {investment.current_price_per_unit}")
                investment.current_price_per_unit = current_nav
                investment.current_total_value = float(investment.current_price_per_unit) * float(investment.unit_quantity)
                
                # Calculate return on investment
                initial_investment = investment.total_invested_amount
                current_value = investment.current_total_value
                investment.return_on_investment = ((current_value - initial_investment) / initial_investment) * 100
                
                # Calculate XIRR
                days_invested = (datetime.now().date() - investment.investment_date).days
                years = days_invested / 365.0
                
                if years > 0:
                    investment.xirr = (((current_value / initial_investment) ** (1 / years)) - 1) * 100
                else:
                    investment.xirr = 0.0
                
                updated_count += 1

                # Log the update
                logger.info(f"Updated {scheme_code} - Current NAV: {current_nav}, Total Value: {investment.current_total_value}, ROI: {investment.return_on_investment:.2f}%, XIRR: {investment.xirr:.2f}%")
        
        # Commit all changes
        db.commit()
        logger.info(f"Updated {updated_count} mutual fund investments")
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating mutual fund values: {str(e)}")
        raise

def get_data_from_investment_summary(db: Session):
    return {
        "common_stocks": [s.stock_symbol for s in db.query(StockSummary).filter(or_(StockSummary.dividend_paying == 0, StockSummary.dividend_paying == None)).all()],
        "stocks_with_dividends": [s.stock_symbol for s in db.query(StockSummary).filter(StockSummary.dividend_paying == 1).all()],
        "mutual_funds": [m.scheme_code for m in db.query(MutualFundSummary).all()],
        "crypto": [c.coin_symbol for c in db.query(CryptoSummary).all()],
        "bullion": list({b.metal_name for b in db.query(BullionSummary).all()})
    }

def get_dividends_data(db: Session):
    results = db.query(DividendSummary.stock_symbol, DividendSummary.total_amount).all()
    return {symbol: price for symbol, price in results}