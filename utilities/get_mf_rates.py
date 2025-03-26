import json
from mftool import Mftool
import redis

# Redis Config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_mutual_fund_rates(scheme_code: str):
    """Fetch Mutual Fund NAV with caching"""
    cache_key = f"mutual_fund:{scheme_code}"
    
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print(f"Using cached data for Mutual Fund ID: {scheme_code}")
        return json.loads(cached_data)

    mf_tool = Mftool()
    try:
        fund_data = mf_tool.get_scheme_quote(scheme_code)

        # Store in Redis with a 24-hour expiry
        redis_client.setex(cache_key, 86400, json.dumps(fund_data))

        return fund_data
    except Exception as e:
        print(f"Error fetching Mutual Fund data: {e}")
        return None
