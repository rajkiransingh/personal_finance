import json
from mftool import Mftool
import redis
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Mutual_fund_rate_fetcher_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("get_mf_rates")

# Redis Config
logger.info("Initialize Redis Client")
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Initialize Mftool
mf = Mftool()

# def get_all_mutual_fund_rates():
#     schemes = mf.get_scheme_codes()
#     for scheme_name, scheme_code in schemes.items():
#         print(f"{scheme_name}: {scheme_code}")

# def get_mutual_fund_rates_by_name(mf_name: str):
#     schemes = mf.get_scheme_codes()
#     for scheme_name, scheme_code in schemes.items():
#         if mf_name in scheme_code:
#             print(f"{scheme_name}: {scheme_code}")
#             print(f"Price of the MF: {get_mutual_fund_rates(scheme_name)}")

def get_mutual_fund_rates_bulk(scheme_code_list: list):
    """Fetch Mutual Fund NAVs for multiple scheme codes with caching"""
    result = {}

    for scheme_code in scheme_code_list:
        cache_key = f"mutual_fund:{scheme_code}"
        cached_data = redis_client.get(cache_key)

        if cached_data:
            logger.info(f"Using cached data for Mutual Fund ID: {scheme_code}")
            result[scheme_code] = json.loads(cached_data)
            continue

        try:
            logger.info(f"Fetching the data from mfTool for: {scheme_code}")
            fund_data = mf.get_scheme_quote(scheme_code)

            # Store in Redis with a 24-hour expiry
            redis_client.setex(cache_key, 86400, json.dumps(fund_data))
            result[scheme_code] = fund_data

        except Exception as e:
            logger.error(f"Error fetching Mutual Fund data for {scheme_code}: {e}")
            result[scheme_code] = None # Store None for this scheme code

    return result

def get_mutual_fund_nav_dict(mf_data: dict):
    """
    Returns a dictionary with mutual fund scheme codes as keys and their NAVs as values
    """
    result = {}
    for scheme_code, mf_info in mf_data.items():
        try:
            if isinstance(mf_info, str):
                mf_info = json.loads(mf_info)
            nav = mf_info.get("nav", "N/A")
            result[scheme_code] = nav
        except Exception as e:
            result[scheme_code] = "Error: " + str(e)
    
    return result

# def get_mutual_fund_rates(scheme_code: str):
#     """Fetch Mutual Fund NAV with caching"""
#     cache_key = f"mutual_fund:{scheme_code}"
    
#     cached_data = redis_client.get(cache_key)
#     if cached_data:
#         print(f"Using cached data for Mutual Fund ID: {scheme_code}")
#         return json.loads(cached_data)

#     try:
#         print(f"Fetching the data from mfTool for: {scheme_code}")
#         fund_data = mf.get_scheme_quote(scheme_code)

#         # Store in Redis with a 24-hour expiry
#         redis_client.setex(cache_key, 86400, json.dumps(fund_data))

#         return fund_data
#     except Exception as e:
#         print(f"Error fetching Mutual Fund data: {e}")
#         return None
