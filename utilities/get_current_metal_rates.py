import requests 
import redis
import os
from bs4 import BeautifulSoup
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Bullion_rate_fetcher_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("get_current_metal_rates")

# Redis Config
logger.info("Setup Redis Client...")
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_current_metal_rates(metal):
    purity = "999"

    """Fetch exchange rate with caching"""
    cache_key = f"{metal}_rate:{purity}"

    # Check Redis cache
    cached_rate = redis_client.get(cache_key)
    if cached_rate:
        logger.info(f"Using cached metal rate for {metal}")
        return int(cached_rate)
    
    # Fetch from API if not cached
    city_rates = {}
    url = os.getenv("METAL_RATES_WEBSITE")

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch data from the website")
    else:
        logger.info("Successfully fetched data from the website")
        
    soup = BeautifulSoup(response.content, 'html.parser')
    target_body = soup.find('table', class_ = 'table-striped').find('tbody')

    if target_body:
        rows = target_body.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 4:
                type = cells[0].text.strip()
                carat = cells[1].text.strip()
                am_rate = cells[2].text.strip()
                pm_rate = cells[3].text.strip()

                if type == metal and carat == purity:
                    city_rates[f"{type} {carat}"] = {
                        'AM': am_rate,
                        'PM': pm_rate
                    }

                    # Store in Redis with a 24-hour expiry
                    redis_client.setex(cache_key, 86400, str(city_rates[f"{metal} {carat}"]['AM']))
                else:
                    logger.warning(f"No matching of {metal} and {purity} found.")
            else:
                logger.error("Target div does not have the expected number of cells.")
            
        return  city_rates[f"{metal} {purity}"]['AM']