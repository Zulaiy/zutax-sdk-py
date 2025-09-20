"""Formatting utilities for Zutax SDK (native).

Provides helpers for currency and percentage formatting and decimal
rounding used across the SDK.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

from ..models.enums import Currency


def format_currency(amount: Decimal, currency: Currency = Currency.NGN) -> str:
    """Format a currency amount with an appropriate symbol and separators.

    Args:
        amount: Decimal amount to format
        currency: Currency enum (defaults to NGN)

    Returns:
        A formatted currency string like "₦1,234.56".
    """
    symbols: Dict[Currency, str] = {
        Currency.NGN: "₦",
        Currency.USD: "$",
        Currency.EUR: "€",
        Currency.GBP: "£",
        Currency.XOF: "CFA",
    }
    symbol = symbols.get(currency, getattr(currency, "value", str(currency)))

    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"


def format_percentage(percentage: Decimal) -> str:
    """Format a percentage with 2 decimal places (e.g., 7.50%)."""
    return f"{percentage:.2f}%"


def calculate_percentage(amount: Decimal, percentage: Decimal) -> Decimal:
    """Calculate the percentage of an amount and round to 2 decimals."""
    result = (amount * percentage) / Decimal("100")
    return round_decimal(result)


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Round a Decimal to the specified number of places using HALF_UP."""
    quantizer = Decimal("0.1") ** places
    return value.quantize(quantizer, rounding=ROUND_HALF_UP)


__all__ = [
    "format_currency",
    "format_percentage",
    "calculate_percentage",
    "round_decimal",
]
