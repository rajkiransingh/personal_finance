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

    # Map currency_id to Redis forex keys
    if currency_id == 2:  # PLN
        key = "forex::PLN-INR"
    elif currency_id == 3:  # USD
        key = "forex::USD-INR"
    else:
        return Decimal("1.0")

    try:
        data = redis_client.get(key)
        if data:
            rate = json.loads(data).get("rate")
            if rate:
                return Decimal(str(rate)).quantize(
                    Decimal("0.00000001"), rounding=ROUND_HALF_UP
                )
    except Exception:
        # Fallback to 1.0 if Redis fails or key missing
        pass

    return Decimal("1.0")
