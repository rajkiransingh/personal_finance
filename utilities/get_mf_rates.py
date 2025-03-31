import json
from mftool import Mftool
import redis

# Redis Config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Mftool
mf = Mftool()

def get_all_mutual_fund_rates():
    schemes = mf.get_scheme_codes()
    for scheme_name, scheme_code in schemes.items():
        print(f"{scheme_name}: {scheme_code}")

def get_mutual_fund_rates_by_name(mf_name: str):
    schemes = mf.get_scheme_codes()
    for scheme_name, scheme_code in schemes.items():
        if mf_name in scheme_code:
            print(f"{scheme_name}: {scheme_code}")

def get_mutual_fund_rates(scheme_code: str):
    """Fetch Mutual Fund NAV with caching"""
    cache_key = f"mutual_fund:{scheme_code}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print(f"Using cached data for Mutual Fund ID: {scheme_code}")
        return json.loads(cached_data)

    try:
        print(f"Fetching the data from mfTool for: {scheme_code}")
        fund_data = mf.get_scheme_quote(scheme_code)

        # Store in Redis with a 24-hour expiry
        redis_client.setex(cache_key, 86400, json.dumps(fund_data))

        return fund_data
    except Exception as e:
        print(f"Error fetching Mutual Fund data: {e}")
        return None
