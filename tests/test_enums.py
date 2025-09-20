"""Tests for FIRS E-Invoice enums and utilities."""

import pytest
from decimal import Decimal

from zutax.models.enums import (
    InvoiceType,
    InvoiceStatus,
    Currency,
    CountryCode,
    PaymentMethod,
    TaxCategory,
    UnitOfMeasure,
)
from zutax.utils import (
    format_currency,
    format_percentage,
    calculate_percentage,
    round_decimal,
)


class TestEnums:
    """Test enum definitions."""
    
    def test_invoice_type_values(self):
        """Test InvoiceType enum values."""
        assert InvoiceType.STANDARD.value == "STANDARD"
        assert InvoiceType.CREDIT.value == "CREDIT"
        assert InvoiceType.DEBIT.value == "DEBIT"
        assert InvoiceType.IMPORT.value == "IMPORT"
    
    def test_invoice_status_values(self):
        """Test InvoiceStatus enum values."""
        assert InvoiceStatus.DRAFT.value == "DRAFT"
        assert InvoiceStatus.SUBMITTED.value == "SUBMITTED"
        assert InvoiceStatus.ACCEPTED.value == "ACCEPTED"
        assert InvoiceStatus.REJECTED.value == "REJECTED"
        assert InvoiceStatus.CANCELLED.value == "CANCELLED"
    
    def test_currency_values(self):
        """Test Currency enum values."""
        assert Currency.NGN.value == "NGN"
        assert Currency.USD.value == "USD"
        assert Currency.EUR.value == "EUR"
        assert Currency.GBP.value == "GBP"
    
    def test_country_values(self):
        """Test CountryCode enum values."""
        assert CountryCode.NG.value == "NG"
        assert CountryCode.US.value == "US"
    
    def test_payment_method_values(self):
        """Test PaymentMethod enum values."""
        assert PaymentMethod.CASH.value == "CASH"
        assert PaymentMethod.BANK_TRANSFER.value == "BANK_TRANSFER"
        assert PaymentMethod.CARD.value == "CARD"
        assert PaymentMethod.CHEQUE.value == "CHEQUE"
        assert PaymentMethod.MOBILE_MONEY.value == "MOBILE_MONEY"
        assert PaymentMethod.OTHER.value == "OTHER"
    
    def test_tax_category_values(self):
        """Test TaxCategory enum values."""
        assert TaxCategory.VAT.value == "VAT"
        assert TaxCategory.EXCISE.value == "EXCISE"
        assert TaxCategory.CUSTOMS.value == "CUSTOMS"
        assert TaxCategory.WITHHOLDING.value == "WITHHOLDING"
    
    def test_unit_of_measure_values(self):
        """Test UnitOfMeasure enum values."""
        assert UnitOfMeasure.PIECE.value == "PCE"
        assert UnitOfMeasure.KILOGRAM.value == "KG"
        assert UnitOfMeasure.GRAM.value == "G"
        assert UnitOfMeasure.LITRE.value == "L"
        assert UnitOfMeasure.MILLILITRE.value == "ML"
        assert UnitOfMeasure.METRE.value == "M"
        assert UnitOfMeasure.SQUARE_METRE.value == "M2"
        assert UnitOfMeasure.CUBIC_METRE.value == "M3"
        assert UnitOfMeasure.HOUR.value == "HR"
        assert UnitOfMeasure.DAY.value == "DAY"
        assert UnitOfMeasure.UNIT.value == "UNIT"
        assert UnitOfMeasure.BOX.value == "BOX"
        assert UnitOfMeasure.PACK.value == "PCK"
    
    
    def test_enum_iteration(self):
        """Test that enums can be iterated."""
        invoice_types = list(InvoiceType)
        assert len(invoice_types) >= 4
        assert InvoiceType.STANDARD in invoice_types
        
        statuses = list(InvoiceStatus)
        assert len(statuses) >= 5
        assert InvoiceStatus.DRAFT in statuses
    
    def test_enum_comparison(self):
        """Test enum comparison."""
        assert InvoiceType.STANDARD == InvoiceType.STANDARD
        assert InvoiceType.STANDARD != InvoiceType.CREDIT
        assert InvoiceStatus.DRAFT != InvoiceStatus.SUBMITTED


class TestUtilities:
    """Test utility functions."""
    
    def test_format_currency_ngn(self):
        """Test formatting Nigerian Naira."""
        assert format_currency(Decimal("1000.00")) == "₦1,000.00"
        assert format_currency(Decimal("1234567.89")) == "₦1,234,567.89"
        assert format_currency(Decimal("0.50")) == "₦0.50"
        assert format_currency(Decimal("-500.00")) == "-₦500.00"
    
    def test_format_currency_usd(self):
        """Test formatting US Dollar."""
        assert format_currency(Decimal("1000.00"), Currency.USD) == "$1,000.00"
        assert format_currency(Decimal("1234567.89"), Currency.USD) == "$1,234,567.89"
    
    def test_format_currency_eur(self):
        """Test formatting Euro."""
        assert format_currency(Decimal("1000.00"), Currency.EUR) == "€1,000.00"
        assert format_currency(Decimal("1234567.89"), Currency.EUR) == "€1,234,567.89"
    
    def test_format_currency_gbp(self):
        """Test formatting British Pound."""
        assert format_currency(Decimal("1000.00"), Currency.GBP) == "£1,000.00"
        assert format_currency(Decimal("1234567.89"), Currency.GBP) == "£1,234,567.89"
    
    def test_format_percentage(self):
        """Test formatting percentages."""
        assert format_percentage(Decimal("7.5")) == "7.50%"
        assert format_percentage(Decimal("10")) == "10.00%"
        assert format_percentage(Decimal("0.5")) == "0.50%"
        assert format_percentage(Decimal("100")) == "100.00%"
        assert format_percentage(Decimal("15.75")) == "15.75%"
    
    def test_calculate_percentage(self):
        """Test percentage calculation."""
        assert calculate_percentage(Decimal("1000"), Decimal("10")) == Decimal("100.00")
        assert calculate_percentage(Decimal("500"), Decimal("7.5")) == Decimal("37.50")
        assert calculate_percentage(Decimal("1234.56"), Decimal("15")) == Decimal("185.18")
        assert calculate_percentage(Decimal("100"), Decimal("0")) == Decimal("0.00")
    
    def test_round_decimal(self):
        """Test decimal rounding."""
        assert round_decimal(Decimal("10.456")) == Decimal("10.46")
        assert round_decimal(Decimal("10.454")) == Decimal("10.45")
        assert round_decimal(Decimal("10.005")) == Decimal("10.01")
        assert round_decimal(Decimal("10")) == Decimal("10.00")
        
        # Test with different decimal places
        assert round_decimal(Decimal("10.456789"), 4) == Decimal("10.4568")
        assert round_decimal(Decimal("10.456789"), 0) == Decimal("10")
    
    def test_decimal_arithmetic_precision(self):
        """Test that decimal arithmetic maintains precision."""
        # This would fail with float
        result = Decimal("0.1") + Decimal("0.2")
        assert result == Decimal("0.3")
        
        # Test multiplication
        result = Decimal("19.99") * Decimal("3")
        assert result == Decimal("59.97")
        
        # Test division
        result = Decimal("100") / Decimal("3")
        rounded = round_decimal(result)
        assert rounded == Decimal("33.33")