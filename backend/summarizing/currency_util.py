import json
from decimal import Decimal, ROUND_HALF_UP
from utilities.common.app_config import config


def get_conversion_rate_to_inr(currency_id: int) -> Decimal:
    """
    Returns the conversion rate from a given currency_id to INR.
    Mapping: 1: INR, 2: PLN, 3: USD
    """
    if currency_id == 1:  # INR
        return Decimal("1.0")

    redis_client = config.redis_client()

    # Map currency_id to Redis forex keys and currency codes
    currency_map = {2: "PLN", 3: "USD"}
    currency_code = currency_map.get(currency_id)
    if not currency_code:
        return Decimal("1.0")

    key = f"forex::{currency_code}-INR"

    try:
        data = redis_client.get(key)
        if data:
            rate = json.loads(data).get("rate")
            if rate:
                return Decimal(str(rate)).quantize(
                    Decimal("0.00000001"), rounding=ROUND_HALF_UP
                )
    except Exception:
        pass

    # On cache miss or expiration, fetch on-demand using ForexExchangeRateFetcher
    try:
        from utilities.forex_exchange_rate_fetcher import forexFetcher
        rate = forexFetcher.get_exchange_rates(currency_code, "INR")
        if rate and rate > Decimal("0"):
            return Decimal(str(rate)).quantize(
                Decimal("0.00000001"), rounding=ROUND_HALF_UP
            )
    except Exception:
        pass

    return Decimal("1.0")
