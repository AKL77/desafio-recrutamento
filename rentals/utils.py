# Utility functions for business logic
# Note: Some functions lack proper documentation

from decimal import Decimal
import config

def calculate_discount(days: int, total: Decimal) -> Decimal:
    """
    Calcular desconto baseado no número de dias de locação
    
    Args:
        days: Número de dias de locação
        total: Total do custo antes do desconto
    
    Returns:
        Valor do desconto
    """

    if days > config.DISCOUNT_THRESHOLD_WEEK:
        return total * Decimal(str(config.DISCOUNT_RATE_WEEK))
    elif days > config.DISCOUNT_THRESHOLD_SHORT:
        return total * Decimal(str(config.DISCOUNT_RATE_SHORT))
    return Decimal('0.00')


def calculate_late_fee(late_days: int, daily_rate: Decimal) -> Decimal:
    return late_days * daily_rate * Decimal(str(config.LATE_FEE_MULTIPLIER))


def validate_rental_dates(start_date, end_date):
    pass

