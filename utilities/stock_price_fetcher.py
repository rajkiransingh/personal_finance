import json
import time

import yfinance as yf

from backend.common.setup import AppConfig, config


class StockPriceFetcher:
    """Utility class to fetch stock prices"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Stock_price_fetcher",
                                             "Stock_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        self.logger.info("Stock price fetcher initialized successfully")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "stock:"

    def get_stock_prices_in_bulk(self, stock_symbol_list):
        stock_data = {}

        for stock_symbol in stock_symbol_list:
            cache_key = f"{self.cache_key_prefix}:{stock_symbol}"
            # Check if data is already in Redis
            if self.redis_client.exists(cache_key):
                try:
                    # Get and parse the JSON data from Redis
                    cached_data = self.redis_client.get(cache_key)
                    stock_data[stock_symbol] = json.loads(cached_data)
                    price = int(stock_data[stock_symbol]["previousClose"])
                    self.logger.info(f"Cache hit: Using cached price for {stock_symbol}: {price}")
                except json.JSONDecodeError:
                    # If JSON is invalid, fetch fresh data
                    self.logger.info(
                        f"Cache miss: No cached price for {stock_symbol}. Trying to fetch the data from API...")
                    self.fetch_and_cache_stock_data(stock_symbol, stock_data)
            else:
                self.fetch_and_cache_stock_data(stock_symbol, stock_data)

                # Add a small delay between API calls to avoid rate limiting
                if len(stock_symbol_list) > 5:
                    time.sleep(1)

        return stock_data

    def fetch_and_cache_stock_data(self, stock_symbol, stock_data_dict):
        cache_key = f"{self.cache_key_prefix}:{stock_symbol}"
        try:
            # Fetch data from Yahoo Finance API
            ticker_info = yf.Ticker(stock_symbol + '.NS').info

            # Extract only the relevant fields to minimize cache size
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
                'twoHundredDayAverageChangePercent': ticker_info.get('twoHundredDayAverageChangePercent', 'N/A'),
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

            # Store in the return dictionary
            stock_data_dict[stock_symbol] = relevant_data

            # Serialize and store data in Redis with expiration
            self.redis_client.setex(
                cache_key,
                self.cache_expiry_in_seconds,
                json.dumps(relevant_data)
            )

            self.logger.info(f"Fetched fresh data for {stock_symbol} and cached it")

        except Exception as e:
            self.logger.error(f"Error fetching data for {stock_symbol}: {e}")
            stock_data_dict[stock_symbol] = {"error": str(e)}


# Global configuration instance
stockFetcher = StockPriceFetcher()
