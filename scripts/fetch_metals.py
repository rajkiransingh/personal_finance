import sys

from utilities.metal_rate_fetcher import get_gold_rate, get_silver_rate

# Add the app root directory to Python path
sys.path.insert(0, '/app')

get_gold_rate()
get_silver_rate()
