import time
from datetime import datetime, UTC
from decimal import Decimal
from typing import Dict

import yfinance as yf
from sqlalchemy.orm import Session

from backend.common.base_fetcher import BaseFetcher
from backend.models.investments.stock import StockInvestment, StockSummary


class StockPriceFetcher(BaseFetcher):
    """Utility class to fetch stock prices"""

    def __init__(self):
        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "stock"

        super().__init__("Stock_price_fetcher", self.cache_key_prefix, self.cache_expiry_in_seconds)
        self.logger.info("Stock price fetcher initialized successfully")

    def get_stock_prices_in_bulk(self, stock_symbol_list: list):
        """
        Fetch stock data for multiple symbols using Yahoo Finance API with Redis caching.
        Reuses standard cache helpers for consistency.
        """
        cached_map = self.get_from_cache(self.cache_key_prefix, stock_symbol_list)
        missing_symbols = [sym for sym, val in cached_map.items() if val is None]
        fetched = {}
        errors = {}

        if missing_symbols:
            self.logger.info(f"Fetching fresh data for {len(missing_symbols)} stock(s): {missing_symbols}")

            for stock_symbol in missing_symbols:
                try:
                    self.logger.info(f"Fetching {stock_symbol} from Yahoo Finance...")
                    ticker_info = yf.Ticker(stock_symbol + ".NS").info

                    relevant_data = {
                        'currentPrice': ticker_info.get('currentPrice', 'N/A'),
                        'website': ticker_info.get('website', 'N/A'),
                        'industry': ticker_info.get('industry', 'N/A'),
                        'sector': ticker_info.get('sector', 'N/A'),
                        'priceHint': ticker_info.get('priceHint', 'N/A'),
                        'previousClose': ticker_info.get('previousClose', 'N/A'),
                        'open': ticker_info.get('open', 'N/A'),
                        'dayLow': ticker_info.get('dayLow', 'N/A'),
                        'dayHigh': ticker_info.get('dayHigh', 'N/A'),
                        'regularMarketPreviousClose': ticker_info.get('regularMarketPreviousClose', 'N/A'),
                        'regularMarketOpen': ticker_info.get('regularMarketOpen', 'N/A'),
                        'regularMarketDayLow': ticker_info.get('regularMarketDayLow', 'N/A'),
                        'regularMarketDayHigh': ticker_info.get('regularMarketDayHigh', 'N/A'),
                        'dividendRate': ticker_info.get('dividendRate', 'N/A'),
                        'dividendYield': ticker_info.get('dividendYield', 'N/A'),
                        'exDividendDate': ticker_info.get('exDividendDate', 'N/A'),
                        'payoutRatio': ticker_info.get('payoutRatio', 'N/A'),
                        'fiveYearAvgDividendYield': ticker_info.get('fiveYearAvgDividendYield', 'N/A'),
                        'beta': ticker_info.get('beta', 'N/A'),
                        'trailingPE': ticker_info.get('trailingPE', 'N/A'),
                        'forwardPE': ticker_info.get('forwardPE', 'N/A'),
                        'volume': ticker_info.get('volume', 'N/A'),
                        'regularMarketVolume': ticker_info.get('regularMarketVolume', 'N/A'),
                        'averageVolume': ticker_info.get('averageVolume', 'N/A'),
                        'averageVolume10days': ticker_info.get('averageVolume10days', 'N/A'),
                        'averageDailyVolume10Day': ticker_info.get('averageDailyVolume10Day', 'N/A'),
                        'bid': ticker_info.get('bid', 'N/A'),
                        'ask': ticker_info.get('ask', 'N/A'),
                        'bidSize': ticker_info.get('bidSize', 'N/A'),
                        'askSize': ticker_info.get('askSize', 'N/A'),
                        'marketCap': ticker_info.get('marketCap', 'N/A'),
                        'fiftyTwoWeekLow': ticker_info.get('fiftyTwoWeekLow', 'N/A'),
                        'fiftyTwoWeekHigh': ticker_info.get('fiftyTwoWeekHigh', 'N/A'),
                        'priceToSalesTrailing12Months': ticker_info.get('priceToSalesTrailing12Months', 'N/A'),
                        'fiftyDayAverage': ticker_info.get('fiftyDayAverage', 'N/A'),
                        'twoHundredDayAverage': ticker_info.get('twoHundredDayAverage', 'N/A'),
                        'trailingAnnualDividendRate': ticker_info.get('trailingAnnualDividendRate', 'N/A'),
                        'trailingAnnualDividendYield': ticker_info.get('trailingAnnualDividendYield', 'N/A'),
                        'currency': ticker_info.get('currency', 'N/A'),
                        'tradeable': ticker_info.get('tradeable', 'N/A'),
                        'enterpriseValue': ticker_info.get('enterpriseValue', 'N/A'),
                        'profitMargins': ticker_info.get('profitMargins', 'N/A'),
                        'floatShares': ticker_info.get('floatShares', 'N/A'),
                        'sharesOutstanding': ticker_info.get('sharesOutstanding', 'N/A'),
                        'heldPercentInsiders': ticker_info.get('heldPercentInsiders', 'N/A'),
                        'heldPercentInstitutions': ticker_info.get('heldPercentInstitutions', 'N/A'),
                        'impliedSharesOutstanding': ticker_info.get('impliedSharesOutstanding', 'N/A'),
                        'bookValue': ticker_info.get('bookValue', 'N/A'),
                        'priceToBook': ticker_info.get('priceToBook', 'N/A'),
                        'lastFiscalYearEnd': ticker_info.get('lastFiscalYearEnd', 'N/A'),
                        'nextFiscalYearEnd': ticker_info.get('nextFiscalYearEnd', 'N/A'),
                        'mostRecentQuarter': ticker_info.get('mostRecentQuarter', 'N/A'),
                        'earningsQuarterlyGrowth': ticker_info.get('earningsQuarterlyGrowth', 'N/A'),
                        'netIncomeToCommon': ticker_info.get('netIncomeToCommon', 'N/A'),
                        'trailingEps': ticker_info.get('trailingEps', 'N/A'),
                        'forwardEps': ticker_info.get('forwardEps', 'N/A'),
                        'lastSplitFactor': ticker_info.get('lastSplitFactor', 'N/A'),
                        'lastSplitDate': ticker_info.get('lastSplitDate', 'N/A'),
                        'enterpriseToRevenue': ticker_info.get('enterpriseToRevenue', 'N/A'),
                        'enterpriseToEbitda': ticker_info.get('enterpriseToEbitda', 'N/A'),
                        '52WeekChange': ticker_info.get('52WeekChange', 'N/A'),
                        'SandP52WeekChange': ticker_info.get('SandP52WeekChange', 'N/A'),
                        'lastDividendValue': ticker_info.get('lastDividendValue', 'N/A'),
                        'lastDividendDate': ticker_info.get('lastDividendDate', 'N/A'),
                        'quoteType': ticker_info.get('quoteType', 'N/A'),
                        'recommendationKey': ticker_info.get('recommendationKey', 'N/A'),
                        'totalCash': ticker_info.get('totalCash', 'N/A'),
                        'totalCashPerShare': ticker_info.get('totalCashPerShare', 'N/A'),
                        'ebitda': ticker_info.get('ebitda', 'N/A'),
                        'totalDebt': ticker_info.get('totalDebt', 'N/A'),
                        'totalRevenue': ticker_info.get('totalRevenue', 'N/A'),
                        'debtToEquity': ticker_info.get('debtToEquity', 'N/A'),
                        'revenuePerShare': ticker_info.get('revenuePerShare', 'N/A'),
                        'grossProfits': ticker_info.get('grossProfits', 'N/A'),
                        'earningsGrowth': ticker_info.get('earningsGrowth', 'N/A'),
                        'revenueGrowth': ticker_info.get('revenueGrowth', 'N/A'),
                        'grossMargins': ticker_info.get('grossMargins', 'N/A'),
                        'ebitdaMargins': ticker_info.get('ebitdaMargins', 'N/A'),
                        'operatingMargins': ticker_info.get('operatingMargins', 'N/A'),
                        'financialCurrency': ticker_info.get('financialCurrency', 'N/A'),
                        'symbol': ticker_info.get('symbol', 'N/A'),
                        'customPriceAlertConfidence': ticker_info.get('customPriceAlertConfidence', 'N/A'),
                        'shortName': ticker_info.get('shortName', 'N/A'),
                        'longName': ticker_info.get('longName', 'N/A'),
                        'regularMarketTime': ticker_info.get('regularMarketTime', 'N/A'),
                        'marketState': ticker_info.get('marketState', 'N/A'),
                        'regularMarketChangePercent': ticker_info.get('regularMarketChangePercent', 'N/A'),
                        'regularMarketPrice': ticker_info.get('regularMarketPrice', 'N/A'),
                        'exchange': ticker_info.get('exchange', 'N/A'),
                        'messageBoardId': ticker_info.get('messageBoardId', 'N/A'),
                        'averageDailyVolume3Month': ticker_info.get('averageDailyVolume3Month', 'N/A'),
                        'fiftyTwoWeekLowChange': ticker_info.get('fiftyTwoWeekLowChange', 'N/A'),
                        'fiftyTwoWeekLowChangePercent': ticker_info.get('fiftyTwoWeekLowChangePercent', 'N/A'),
                        'fiftyTwoWeekRange': ticker_info.get('fiftyTwoWeekRange', 'N/A'),
                        'fiftyTwoWeekHighChange': ticker_info.get('fiftyTwoWeekHighChange', 'N/A'),
                        'fiftyTwoWeekHighChangePercent': ticker_info.get('fiftyTwoWeekHighChangePercent', 'N/A'),
                        'fiftyTwoWeekChangePercent': ticker_info.get('fiftyTwoWeekChangePercent', 'N/A'),
                        'earningsTimestamp': ticker_info.get('earningsTimestamp', 'N/A'),
                        'earningsTimestampStart': ticker_info.get('earningsTimestampStart', 'N/A'),
                        'earningsTimestampEnd': ticker_info.get('earningsTimestampEnd', 'N/A'),
                        'isEarningsDateEstimate': ticker_info.get('isEarningsDateEstimate', 'N/A'),
                        'epsTrailingTwelveMonths': ticker_info.get('epsTrailingTwelveMonths', 'N/A'),
                        'epsForward': ticker_info.get('epsForward', 'N/A'),
                        'fiftyDayAverageChange': ticker_info.get('fiftyDayAverageChange', 'N/A'),
                        'fiftyDayAverageChangePercent': ticker_info.get('fiftyDayAverageChangePercent', 'N/A'),
                        'twoHundredDayAverageChange': ticker_info.get('twoHundredDayAverageChange', 'N/A'),
                        'twoHundredDayAverageChangePercent': ticker_info.get('twoHundredDayAverageChangePercent',
                                                                             'N/A'),
                        'sourceInterval': ticker_info.get('sourceInterval', 'N/A'),
                        'exchangeDataDelayedBy': ticker_info.get('exchangeDataDelayedBy', 'N/A'),
                        'cryptoTradeable': ticker_info.get('cryptoTradeable', 'N/A'),
                        'hasPrePostMarketData': ticker_info.get('hasPrePostMarketData', 'N/A'),
                        'firstTradeDateMilliseconds': ticker_info.get('firstTradeDateMilliseconds', 'N/A'),
                        'regularMarketChange': ticker_info.get('regularMarketChange', 'N/A'),
                        'regularMarketDayRange': ticker_info.get('regularMarketDayRange', 'N/A'),
                        'fullExchangeName': ticker_info.get('fullExchangeName', 'N/A'),
                        'trailingPegRatio': ticker_info.get('trailingPegRatio', 'N/A')
                    }

                    fetched[stock_symbol] = relevant_data
                    self.logger.info(f"✅ {stock_symbol}: {relevant_data['currentPrice']} cached")

                except Exception as e:
                    self.logger.error(f"❌ Error fetching {stock_symbol}: {e}")
                    fetched[stock_symbol] = None
                    errors[stock_symbol] = str(e)

                # optional throttling
                if len(missing_symbols) > 5:
                    time.sleep(1)

            # Cache only successful fetches
            to_cache = {s: v for s, v in fetched.items() if v is not None}
            if to_cache:
                try:
                    self.set_cache(self.cache_key_prefix, to_cache)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to cache stock data: {e}")

        # Merge cached and fetched data
        final_map = {}
        for sym in stock_symbol_list:
            cached_val = cached_map.get(sym)
            if cached_val is not None:
                final_map[sym] = cached_val
            else:
                final_map[sym] = fetched.get(sym)

        return {"data": final_map, "errors": errors}

    def update_stock_investments(self, db: Session, stock_data: Dict, dividend_data=None) -> Dict:
        if dividend_data is None:
            dividend_data = {}

        today = datetime.now(UTC)
        updated_count = 0
        errors = []
        try:
            for symbol, data in stock_data.items():
                # Get all bullion investments that need updating
                stock_investments = (
                    db.query(StockInvestment)
                    .filter(StockInvestment.stock_symbol == symbol, StockInvestment.transaction_type == 'BUY')
                    .all()
                )
                price = Decimal(
                    data["previousClose"] if data.get("currentPrice") == "N/A" else data["currentPrice"]
                )
                dividend_amount = dividend_data.get(symbol, 0)
                currency_symbol = "₹"
                for investment in stock_investments:
                    try:
                        self.logger.info(
                            f"Updating Stock investment data for {data['shortName']}")
                        self.logger.info(
                            f"Current price for stock: {symbol} in INR is: {currency_symbol}{price}")

                        current_value = float(price * investment.stock_quantity) + dividend_amount
                        self.logger.info(
                            f"We got the current value {current_value} for stock: {symbol} by adding: {float(price * investment.stock_quantity)} and dividend: {dividend_amount}")
                        initial_investment = investment.total_invested_amount
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Calculate XIRR (simplified version)
                        days_invested = (today.date() - investment.investment_date).days
                        years = days_invested / 365.0

                        # Updating the investment table
                        investment.current_price_per_stock = price
                        investment.current_total_value = current_value
                        investment.return_on_investment = roi_value

                        if years >= 1:
                            investment.xirr = (((current_value / initial_investment) ** (1 / years)) - 1) * 100
                        else:
                            investment.xirr = ((current_value - initial_investment) / initial_investment) * 100

                        updated_count += 1
                        self.logger.debug(
                            f"Updated {data['shortName']} with price: {currency_symbol}{price}")

                    except Exception as e:
                        self.logger.error(f"Failed to update {data['shortName']} investment: {e}")

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} stock investments")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update stock investments: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }

    def update_stock_summary(self, db: Session, stock_data: Dict, dividend_data=None) -> Dict:
        if dividend_data is None:
            dividend_data = {}
        updated_count = 0
        errors = []

        try:
            for symbol, data in stock_data.items():

                # Get all stock investments that need updating
                mf_summaries = db.query(StockSummary).filter(StockSummary.stock_symbol == symbol).all()
                investments = db.query(StockInvestment).filter(
                    StockInvestment.stock_symbol == symbol).all()

                price = float(
                    data["previousClose"] if data.get("currentPrice") == "N/A" else data["currentPrice"]
                )
                dividend_amount = dividend_data.get(symbol, 0)
                currency_symbol = "₹"
                for summary in mf_summaries:
                    try:
                        self.logger.info(f"Updating Stock Summary data for {data['shortName']}")
                        self.logger.info(
                            f"Current price for stock: {symbol} in INR is: {currency_symbol}{price}")

                        current_value = round((price * summary.total_quantity), 2) + dividend_amount
                        self.logger.info(
                            f"We got the current value {current_value} for stock: {symbol} by adding: {float(price * summary.total_quantity)} and dividend: {dividend_amount}")

                        initial_investment = summary.total_cost
                        roi_value = ((current_value - initial_investment) /
                                     initial_investment * 100)

                        # Weighted average XIRR calculation from Bullion Investment
                        relevant_investments = [
                            inv for inv in investments if inv.stock_symbol == symbol
                        ]

                        if relevant_investments:
                            total_weighted_xirr = sum(
                                (investment.total_invested_amount / initial_investment) * investment.xirr
                                for investment in relevant_investments
                            )
                            self.logger.info(
                                f"Total weighted xirr calculated is: {round(total_weighted_xirr, 2)}%")
                        else:
                            total_weighted_xirr = 0.0

                        # Update Summary table
                        summary.current_price_per_unit = price
                        summary.current_value = current_value
                        summary.roi = roi_value
                        summary.xirr = total_weighted_xirr
                        summary.last_updated = datetime.now(UTC)

                        updated_count += 1
                        self.logger.info(
                            f"Updated {data['shortName']} investment summary with price: {currency_symbol}{price}")

                    except Exception as e:
                        error_msg = f"Error updating investment summary {summary.id}: {e}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)

            # Commit all changes
            db.commit()
            self.logger.info(f"Updated {updated_count} stock investment summary")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors
            }

        except Exception as e:
            db.rollback()
            error_msg = f"Failed to update stock investment summary: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "updated_count": 0
            }


# Global configuration instance
stockFetcher = StockPriceFetcher()
