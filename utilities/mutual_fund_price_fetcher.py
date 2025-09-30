import json
import os

import requests

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

        # Initialize env variables
        self.rapid_api_host = os.getenv("RAPID_API_MF_HOST")
        self.base_url = os.getenv("RAPID_API_MF_URL")
        self.rapid_api_key = os.getenv("RAPID_MF_API_KEY")

        # Load config data from environment
        self.cache_expiry_in_seconds = 86400
        self.cache_key_prefix = "mutual-fund:"

        self.logger.info("Mutual Fund price fetcher initialized successfully")

    def get_mutual_fund_rates_bulk(self, scheme_code_list: list):
        """Fetch Mutual Fund NAVs for multiple scheme codes with caching"""
        result = {}

        for scheme_code in scheme_code_list:
            cache_key = f"{self.cache_key_prefix}:{scheme_code}"
            cached_data = self.redis_client.get(cache_key)
            cached_info = json.loads(cached_data)

            if cached_info:
                self.logger.info(
                    f"Cache hit: Using cached data for Mutual Fund: {cached_info['Fund_Name']} with value: {cached_info['NAV']}")
                result[scheme_code] = cached_info
                continue

            try:
                self.logger.info(f"Fetching the data from rapid API for scheme code: {scheme_code}")
                endpoint = f"{self.base_url}{scheme_code}"

                headers = {
                    'x-rapidapi-host': self.rapid_api_host,
                    'x-rapidapi-key': self.rapid_api_key
                }

                response = requests.get(endpoint, headers=headers, timeout=30)
                response.raise_for_status()

                data = response.json()
                self.logger.info(
                    f"Fetched {data['data']['Fund_Name']} with scheme code: {scheme_code}:: nav - {data['data']['NAV']}")

                # Store in Redis with a 24-hour expiry
                try:
                    self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(data['data']))
                    self.logger.info(f"Cached mutual fund nav of - {data['data']['Fund_Name']} in Redis")
                except Exception as e:
                    self.logger.warning(f"Failed to cache nav of - {data['data']['Fund_Name']}:: Error - {e}")

                result[scheme_code] = data

            except Exception as e:
                self.logger.error(
                    f"Cache miss: Error fetching Mutual Fund data for scheme code: {scheme_code} Error - {e}")
                result[scheme_code] = None  # Store None for this scheme code

        return result

    # def get_mutual_fund_nav_dict(self, mf_data: dict):
    #     """
    #     Returns a dictionary with mutual fund scheme codes as keys and their NAVs as values
    #     """
    #     result = {}
    #     for scheme_code, mf_info in mf_data.items():
    #         try:
    #             if isinstance(mf_info, str):
    #                 mf_info = json.loads(mf_info)
    #             nav = mf_info.get("nav", "N/A")
    #             result[scheme_code] = nav
    #             self.logger.info(f"Fetch success: Data for scheme code: {scheme_code} has NAV: {nav}")
    #         except Exception as e:
    #             self.logger.error(f"Fetch error: Error fetching Mutual Fund data for {scheme_code}: {e}")
    #             result[scheme_code] = "Error: " + str(e)
    #
    #     return result

    # def get_mutual_fund_rates(self, scheme_code: str):
    #     """Fetch Mutual Fund NAV with caching"""
    #     cache_key = f"{self.cache_key_prefix}:{scheme_code}"
    #
    #     cached_data = self.redis_client.get(cache_key)
    #     if cached_data:
    #         print(f"Using cached data for Mutual Fund ID: {scheme_code}")
    #         return json.loads(cached_data)
    #
    #     try:
    #         print(f"Fetching the data from mfTool for: {scheme_code}")
    #         fund_data = self.mf.get_scheme_quote(scheme_code)
    #
    #         # Store in Redis with a 24-hour expiry
    #         self.redis_client.setex(cache_key, self.cache_expiry_in_seconds, json.dumps(fund_data))
    #
    #         return fund_data
    #     except Exception as e:
    #         print(f"Error fetching Mutual Fund data: {e}")
    #         return None


# Global configuration instance
mutualFundFetcher = MutualFundPriceFetcher()
