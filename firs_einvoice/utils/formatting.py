"""Formatting utilities for FIRS E-Invoice SDK."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from ..models.enums import Currency


def format_currency(amount: Decimal, currency: Currency = Currency.NGN) -> str:
    """
    Format currency amount with appropriate symbol.
    
    Args:
        amount: The amount to format
        currency: The currency type
        
    Returns:
        Formatted currency string
    """
    # Currency symbols
    symbols = {
        Currency.NGN: "₦",
        Currency.USD: "$", 
        Currency.EUR: "€",
        Currency.GBP: "£",
    }
    
    symbol = symbols.get(currency, currency.value)
    
    # Format with thousands separator
    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    else:
        return f"{symbol}{amount:,.2f}"


def format_percentage(percentage: Decimal) -> str:
    """
    Format percentage with 2 decimal places.
    
    Args:
        percentage: The percentage value
        
    Returns:
        Formatted percentage string
    """
    return f"{percentage:.2f}%"


def calculate_percentage(amount: Decimal, percentage: Decimal) -> Decimal:
    """
    Calculate percentage of an amount.
    
    Args:
        amount: The base amount
        percentage: The percentage rate
        
    Returns:
        Calculated percentage amount
    """
    result = (amount * percentage) / Decimal("100")
    return round_decimal(result)


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """
    Round decimal to specified places using banker's rounding.
    
    Args:
        value: The decimal value to round
        places: Number of decimal places
        
    Returns:
        Rounded decimal value
    """
    quantizer = Decimal('0.1') ** places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)