from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class FinancialCalculator:
    @staticmethod
    def calculate_roi(current_value, initial_investment) -> float:
        """Calculates Return on Investment (ROI) percentage."""
        try:
            c_val = float(current_value)
            init_inv = float(initial_investment)
            if init_inv == 0:
                return 0.0
            return ((c_val - init_inv) / init_inv) * 100
        except Exception:
            return 0.0

    @staticmethod
    def calculate_xirr(current_value, initial_investment, investment_date: date,
                       current_date: date) -> float:
        """
        Calculates a simplified XIRR (Annualized Return).
        """
        try:
            c_val = float(current_value)
            init_inv = float(initial_investment)
            if init_inv == 0:
                return 0.0

            days_invested = (current_date - investment_date).days
            years = days_invested / 365.0

            if c_val <= 0:
                return -100.0 if init_inv > 0 else 0.0

            if years < 1:
                return ((c_val - init_inv) / init_inv) * 100

            return (((c_val / init_inv) ** (1.0 / years)) - 1.0) * 100
        except Exception:
            return 0.0

    @staticmethod
    def round2(x) -> float:
        """Standardized rounding wrapper."""
        try:
            return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        except Exception:
            return 0.0
