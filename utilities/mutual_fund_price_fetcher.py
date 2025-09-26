import json
import os

import yfinance as yf
from mftool import Mftool

from backend.common.setup import AppConfig, config


class MutualFundPriceFetcher:
    """Utility class to fetch mutual fund prices"""

    def __init__(self):
        # Set up logging using the common config
        self.logger = AppConfig.setup_logger(config, "Mutual_Fund_price_fetcher",
                                             "Mutual_Fund_price_fetcher_logs.log")

        # Get Redis client
        self.logger.info("Initializing Redis Client")
        self.redis_client = AppConfig.redis_client(config)

        # Initialize Mftool
        self.logger.info("Initializing MF-Tool")
        try:
            self.mf = Mftool()
        except Exception as e:
            self.logger.error(f"Could not initialize MF-Tool: {e}")

        self.logger.info("Mutual Fund price fetcher initialized successfully")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "mutual-fund:"
        self.nse_url = os.getenv("NSE_WEBSITE_URL")
        self.max_retries = 3
        self.delay = 5

    def get_all_mutual_fund_rates(self):
        schemes = self.mf.get_scheme_codes()
        for scheme_name, scheme_code in schemes.items():
            print(f"{scheme_name}: {scheme_code}")

    def get_mutual_fund_rates_by_name(self, mf_name: str):
        schemes = self.mf.get_scheme_codes()
        for scheme_name, scheme_code in schemes.items():
            if mf_name in scheme_code:
                print(f"{scheme_name}: {scheme_code}")
                print(f"Price of the MF: {self.get_mutual_fund_rates(scheme_name)}")

    def get_mutual_fund_rates_bulk(self, scheme_code_list: list):
        """Fetch Mutual Fund NAVs for multiple scheme codes with caching"""
        result = {}

        for scheme_code in scheme_code_list:
            cache_key = f"{self.cache_key_prefix}:{scheme_code}"
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                self.logger.info(f"Cache hit: Using cached data for Mutual Fund ID: {scheme_code}")
                result[scheme_code] = json.loads(cached_data)
                continue

            try:
                self.logger.info(f"Fetching the data from mfTool for: {scheme_code}")
                fund_data = yf.Ticker(scheme_code).history(period="1d")

                # Store in Redis with a 24-hour expiry
                self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(fund_data))
                result[scheme_code] = fund_data

            except Exception as e:
                self.logger.error(f"Cache miss: Error fetching Mutual Fund data for {scheme_code}: {e}")
                result[scheme_code] = None  # Store None for this scheme code

        return result

    def get_mutual_fund_nav_dict(self, mf_data: dict):
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
                self.logger.info(f"Fetch success: Data for scheme code: {scheme_code} has NAV: {nav}")
            except Exception as e:
                self.logger.error(f"Fetch error: Error fetching Mutual Fund data for {scheme_code}: {e}")
                result[scheme_code] = "Error: " + str(e)

        return result

    def get_mutual_fund_rates(self, scheme_code: str):
        """Fetch Mutual Fund NAV with caching"""
        cache_key = f"{self.cache_key_prefix}:{scheme_code}"

        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            print(f"Using cached data for Mutual Fund ID: {scheme_code}")
            return json.loads(cached_data)

        try:
            print(f"Fetching the data from mfTool for: {scheme_code}")
            fund_data = self.mf.get_scheme_quote(scheme_code)

            # Store in Redis with a 24-hour expiry
            self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(fund_data))

            return fund_data
        except Exception as e:
            print(f"Error fetching Mutual Fund data: {e}")
            return None
