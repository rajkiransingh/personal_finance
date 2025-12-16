from datetime import date
from decimal import Decimal, ROUND_HALF_UP

class FinancialCalculator:
    @staticmethod
    def calculate_roi(current_value: float, initial_investment: float) -> float:
        """Calculates Return on Investment (ROI) percentage."""
        if initial_investment == 0:
            return 0.0
        return ((current_value - initial_investment) / initial_investment) * 100

    @staticmethod
    def calculate_xirr(current_value: float, initial_investment: float, investment_date: date, current_date: date) -> float:
        """
        Calculates a simplified XIRR (Annualized Return).
        """
        if initial_investment == 0:
            return 0.0
            
        days_invested = (current_date - investment_date).days
        years = days_invested / 365.0

        if current_value <= 0:
            return -100.0 if initial_investment > 0 else 0.0

        if years < 1:
            return ((current_value - initial_investment) / initial_investment) * 100
            
        return (((current_value / initial_investment) ** (1 / years)) - 1) * 100

    @staticmethod
    def round2(x) -> float:
        """Standardized rounding wrapper."""
        try:
            return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        except Exception:
            return 0.0
