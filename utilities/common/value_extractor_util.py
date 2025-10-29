from decimal import Decimal, ROUND_HALF_UP


# ===============================================================
# 🔧 Helper Utilities
# ===============================================================
def round2(x) -> float:
    """Round to 2 decimals with consistent HALF_UP behavior."""
    try:
        return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        return 0.0


def extract_current_value(entry) -> float:
    """Extract current_value field from SQLAlchemy model, dict, or numeric."""
    if entry is None:
        return 0.0
    if isinstance(entry, (int, float)):
        return float(entry)
    if isinstance(entry, dict):
        return float(entry.get("current_value", 0.0))
    return float(getattr(entry, "current_value", 0.0) or 0.0)


def sum_current_values(entries) -> float:
    """Sum current_value for list or single entry."""
    if not entries:
        return 0.0
    if isinstance(entries, list):
        return sum(extract_current_value(e) for e in entries)
    return extract_current_value(entries)
