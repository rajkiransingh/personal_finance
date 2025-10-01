import sys

from utilities.forex_exchange_rate_fetcher import ForexExchangeRateFetcher as fEx, forexFetcher

sys.path.insert(0, '/app')

# Get Forex Data
fEx.get_exchange_rates(forexFetcher, "USD", "INR")
fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
fEx.get_exchange_rates(forexFetcher, "USD", "PLN")
