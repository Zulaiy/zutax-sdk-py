"""Tests for FIRS E-Invoice validation."""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from firs_einvoice import FIRSClient, Invoice, LineItem
from firs_einvoice.schemas.validators import (
    validate_tin,
    validate_phone,
    validate_email,
    validate_hsn_code,
    validate_invoice_number,
    validate_business_id,
)
from firs_einvoice.models.enums import InvoiceType, UnitOfMeasure


class TestFieldValidators:
    """Test individual field validators."""
    
    def test_validate_tin_valid(self):
        """Test valid TIN validation."""
        valid_tins = [
            "12345678901",
            "98765432109",
            "11111111111",
        ]
        for tin in valid_tins:
            is_valid, error = validate_tin(tin)
            assert is_valid is True
            assert error is None
    
    def test_validate_tin_invalid(self):
        """Test invalid TIN validation."""
        invalid_tins = [
            "123",  # Too short
            "123456789012345",  # Too long
            "abcdefghijk",  # Non-numeric
            "",  # Empty
            "1234 5678 901",  # Contains spaces
        ]
        for tin in invalid_tins:
            is_valid, error = validate_tin(tin)
            assert is_valid is False
            assert error is not None
    
    def test_validate_phone_valid(self):
        """Test valid Nigerian phone number validation."""
        valid_phones = [
            "+2348012345678",
            "+2347012345678",
            "+2348112345678",
            "+2349012345678",
            "08012345678",
            "07012345678",
            "08112345678",
            "09012345678",
        ]
        for phone in valid_phones:
            is_valid, error = validate_phone(phone)
            assert is_valid is True
            assert error is None
    
    def test_validate_phone_invalid(self):
        """Test invalid phone number validation."""
        invalid_phones = [
            "+2341234567890",  # Wrong prefix
            "+234801234567",  # Too short
            "+23480123456789",  # Too long
            "1234567890",  # No country code
            "+1234567890",  # Wrong country
            "080-1234-5678",  # Contains dashes
        ]
        for phone in invalid_phones:
            is_valid, error = validate_phone(phone)
            assert is_valid is False
            assert error is not None
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@company.co.ng",
            "info+tag@domain.org",
            "admin@sub.domain.com",
        ]
        for email in valid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is True
            assert error is None
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user @domain.com",
            "user@domain",
            "",
        ]
        for email in invalid_emails:
            is_valid, error = validate_email(email)
            assert is_valid is False
            assert error is not None
    
    def test_validate_hsn_code_valid(self):
        """Test valid HSN code validation."""
        valid_codes = [
            "8471",  # 4 digits
            "847130",  # 6 digits
            "84713000",  # 8 digits
            "9018",  # Medical equipment
            "9984",  # Software services
        ]
        for code in valid_codes:
            is_valid, error = validate_hsn_code(code)
            assert is_valid is True
            assert error is None
    
    def test_validate_hsn_code_invalid(self):
        """Test invalid HSN code validation."""
        invalid_codes = [
            "123",  # Too short
            "123456789",  # Too long
            "12345",  # Odd length
            "ABCD",  # Non-numeric
            "",  # Empty
        ]
        for code in invalid_codes:
            is_valid, error = validate_hsn_code(code)
            assert is_valid is False
            assert error is not None
    
    def test_validate_invoice_number_valid(self):
        """Test valid invoice number validation."""
        valid_numbers = [
            "INV-001",
            "INV-2024-001",
            "INVOICE_12345",
            "CN-001",
            "2024/INV/001",
        ]
        for number in valid_numbers:
            is_valid, error = validate_invoice_number(number)
            assert is_valid is True
            assert error is None
    
    def test_validate_invoice_number_invalid(self):
        """Test invalid invoice number validation."""
        invalid_numbers = [
            "",  # Empty
            "INV#001",  # Invalid character
            "INV 001",  # Contains space (assuming spaces not allowed)
            "A" * 51,  # Too long
        ]
        for number in invalid_numbers:
            is_valid, error = validate_invoice_number(number)
            assert is_valid is False
            assert error is not None
    
    def test_validate_business_id_valid(self):
        """Test valid business ID validation."""
        valid_ids = [
            "BUS-001",
            "COMPANY-12345",
            "UUID-123e4567-e89b",
            "REG_2024_001",
        ]
        for bus_id in valid_ids:
            is_valid, error = validate_business_id(bus_id)
            assert is_valid is True
            assert error is None
    
    def test_validate_business_id_invalid(self):
        """Test invalid business ID validation."""
        invalid_ids = [
            "",  # Empty
            "ID",  # Too short
            "A" * 101,  # Too long
        ]
        for bus_id in invalid_ids:
            is_valid, error = validate_business_id(bus_id)
            assert is_valid is False
            assert error is not None


class TestInvoiceValidation:
    """Test invoice-level validation."""
    
    def test_validate_complete_invoice(self, client, sample_supplier, sample_customer,
                                      line_item_builder):
        """Test validation of a complete invoice."""
        # Create line items
        line_item = (line_item_builder
                    .with_description("Test Product")
                    .with_hsn_code("8471")
                    .with_quantity(5, UnitOfMeasure.PIECE)
                    .with_unit_price(Decimal("100.00"))
                    .with_tax(Decimal("7.5"))
                    .build())
        
        # Create invoice
        invoice = Invoice(
            invoice_number="INV-TEST-001",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[line_item],
        )
        
        # Validate
        result = client.validate_invoice(invoice)
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_invoice_missing_required(self, client, sample_supplier):
        """Test validation with missing required fields."""
        # Create invoice without customer
        with pytest.raises(ValidationError) as exc_info:
            Invoice(
                invoice_number="INV-TEST-002",
                invoice_date=datetime.now(),
                invoice_type=InvoiceType.STANDARD,
                supplier=sample_supplier,
                # customer missing
                line_items=[],
            )
        assert "customer" in str(exc_info.value).lower()
    
    def test_validate_invoice_invalid_tin(self, client, sample_address):
        """Test validation with invalid TIN."""
        from firs_einvoice import Party
        
        with pytest.raises(ValidationError) as exc_info:
            invalid_party = Party(
                business_id="INVALID-001",
                tin="123",  # Invalid TIN
                name="Invalid Company",
                email="test@invalid.com",
                phone="+2348012345678",
                address=sample_address,
            )
        assert "tin" in str(exc_info.value).lower()
    
    def test_validate_line_item_negative_quantity(self):
        """Test validation with negative quantity."""
        with pytest.raises(ValidationError) as exc_info:
            LineItem(
                description="Invalid Item",
                hsn_code="8471",
                quantity=Decimal("-5"),  # Negative
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
            )
        assert "quantity" in str(exc_info.value).lower()
    
    def test_validate_line_item_invalid_tax_rate(self):
        """Test validation with invalid tax rate."""
        with pytest.raises(ValidationError) as exc_info:
            LineItem(
                description="Invalid Tax Item",
                hsn_code="8471",
                quantity=Decimal("1"),
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("150"),  # Over 100%
            )
        assert "tax_rate" in str(exc_info.value).lower()
    
    def test_validate_invoice_computed_fields(self, client, sample_supplier, 
                                             sample_customer, line_item_builder):
        """Test that computed fields don't cause validation errors."""
        # Create line items with discounts and taxes
        item1 = (line_item_builder
                .with_description("Product 1")
                .with_hsn_code("8471")
                .with_quantity(10, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("100.00"))
                .with_discount_percent(Decimal("10"))
                .with_tax(Decimal("7.5"))
                .build())
        
        line_item_builder.reset()
        item2 = (line_item_builder
                .with_description("Product 2")
                .with_hsn_code("9018")  # Medical equipment
                .with_quantity(5, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("200.00"))
                .with_tax_exemption("Medical equipment - VAT exempt")
                .build())
        
        # Create invoice
        invoice = Invoice(
            invoice_number="INV-TEST-003",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[item1, item2],
        )
        
        # Validate - should not fail due to computed fields
        result = client.validate_invoice(invoice)
        assert result.valid is True
        
        # Verify computed fields are calculated correctly
        assert invoice.subtotal == Decimal("2000.00")  # 1000 + 1000
        assert invoice.total_discount == Decimal("100.00")  # 10% of 1000
        assert invoice.total_tax == Decimal("67.500")  # 7.5% of 900
        assert invoice.total_amount == Decimal("1967.500")  # 1900 + 67.5