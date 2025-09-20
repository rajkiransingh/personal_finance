import json
import time

from mftool import Mftool
import yfinance as yf
import redis
import logging
import sys
import os

# Create logs directory if it doesn't exist
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

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

# def initialize_mftool_with_retry(max_retries=3, delay=5):
#     for attempt in range(max_retries):
#         try:
#             logger.info(f"Initializing MF-Tool (attempt {attempt + 1})")
#             mf = Mftool()
#             logger.info("MF-Tool initialized successfully")
#             return mf
#         except Exception as e:
#             logger.error(f"Failed to initialize MF-Tool (attempt {attempt + 1}): {e}")
#             if attempt < max_retries - 1:
#                 logger.info(f"Retrying in {delay} seconds...")
#                 time.sleep(delay)
#             else:
#                 logger.error("Max retries reached. Unable to initialize MF-Tool")
#                 raise
#
# # Initialize Mftool
# logger.info("Initializing MF-Tool")
# try:
#     mf = initialize_mftool_with_retry()
# except Exception as e:
#     logger.error(f"Could not initialize MF-Tool: {e}")
#



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
            fund_data = yf.Ticker(scheme_code).history(period="1d")

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
