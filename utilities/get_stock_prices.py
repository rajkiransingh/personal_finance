from nsepython import *

def get_stock_prices(stock_symbol_list):
    stock_prices = {}
    for symbol in stock_symbol_list:
        try:
            last_price = nse_eq(symbol)['priceInfo']['lastPrice']
            stock_prices[symbol] = last_price
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return stock_prices
