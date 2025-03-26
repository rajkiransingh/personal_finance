import redis
import os
import requests
from decimal import Decimal
from dotenv import load_dotenv

def get_exchange_rates_old(api_key, from_currency, to_currency):
    try:
        OPEN_EXCHANGE_API_URL = "https://v6.exchangerate-api.com/v6/"
        url = f'{OPEN_EXCHANGE_API_URL}{api_key}/pair/{from_currency}/{to_currency}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return Decimal(data['conversion_rate', 1.0])
        else:
            print(f"Error fetching exchange rates. Status Code: {response.status_code}")
            return 1.0
        
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return 1.0


# Load API keys
load_dotenv()

# Redis Config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_exchange_rates(from_currency, to_currency):
    """Fetch exchange rate with caching"""
    cache_key = f"exchange_rate:{from_currency}:{to_currency}"
    
    # Check Redis cache
    cached_rate = redis_client.get(cache_key)
    if cached_rate:
        print(f"Using cached exchange rate for {from_currency} to {to_currency}")
        return Decimal(cached_rate)

    # Fetch from API if not cached
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
    
    try:
        print(f"Fetching exchange rate for {from_currency} to {to_currency}")
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            exchange_rate = Decimal(data.get('conversion_rate', 1.0))

            # Store in Redis with a 24-hour expiry
            redis_client.setex(cache_key, 86400, str(exchange_rate))

            return exchange_rate
        else:
            print(f"Error fetching exchange rates. Status Code: {response.status_code}")
            return Decimal(1.0)
    
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return Decimal(1.0)

