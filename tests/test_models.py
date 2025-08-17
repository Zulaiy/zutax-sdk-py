"""Tests for FIRS E-Invoice models."""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from firs_einvoice.models import (
    Invoice,
    Party,
    Address,
    LineItem,
)
from firs_einvoice.models.enums import (
    CountryCode,
    Currency,
    InvoiceType,
    InvoiceStatus,
    UnitOfMeasure,
    TaxCategory,
)


class TestAddress:
    """Test Address model."""
    
    def test_valid_address(self):
        """Test creating a valid address."""
        from firs_einvoice.models.enums import StateCode
        address = Address(
            street="123 Main St",
            city="Lagos",
            state_code=StateCode.LA,
            postal_code="100001",
            country_code=CountryCode.NG,
        )
        assert address.street == "123 Main St"
        assert address.city == "Lagos"
        assert address.country_code == CountryCode.NG
    
    def test_optional_fields(self):
        """Test address with optional fields."""
        from firs_einvoice.models.enums import StateCode
        address = Address(
            street="456 Test Ave",
            city="Abuja",
            state_code=StateCode.FC,
            country_code=CountryCode.NG,
        )
        assert address.postal_code is None
        assert address.street2 is None
    
    def test_invalid_country(self):
        """Test address with invalid country."""
        from firs_einvoice.models.enums import StateCode
        with pytest.raises(ValidationError):
            Address(
                street="789 Error St",
                city="Test City",
                state_code=StateCode.LA,
                country_code="INVALID",
            )


class TestParty:
    """Test Party model."""
    
    def test_valid_party(self, sample_address):
        """Test creating a valid party."""
        party = Party(
            business_id="PARTY-001",
            tin="12345678901",
            name="Test Company Ltd",
            email="test@company.com",
            phone="+2348012345678",
            address=sample_address,
        )
        assert party.business_id == "PARTY-001"
        assert party.tin == "12345678901"
        assert party.name == "Test Company Ltd"
    
    def test_invalid_tin(self, sample_address):
        """Test party with invalid TIN."""
        with pytest.raises(ValidationError) as exc_info:
            Party(
                business_id="PARTY-002",
                tin="123",  # Too short
                name="Invalid TIN Company",
                email="test@invalid.com",
                phone="+2348012345678",
                address=sample_address,
            )
        assert "tin" in str(exc_info.value)
    
    def test_invalid_email(self, sample_address):
        """Test party with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            Party(
                business_id="PARTY-003",
                tin="12345678901",
                name="Invalid Email Company",
                email="not-an-email",
                phone="+2348012345678",
                address=sample_address,
            )
        assert "email" in str(exc_info.value).lower()
    
    def test_invalid_phone(self, sample_address):
        """Test party with invalid Nigerian phone number."""
        with pytest.raises(ValidationError) as exc_info:
            Party(
                business_id="PARTY-004",
                tin="12345678901",
                name="Invalid Phone Company",
                email="test@phone.com",
                phone="123456",  # Invalid format
                address=sample_address,
            )
        assert "phone" in str(exc_info.value).lower()


class TestLineItem:
    """Test LineItem model."""
    
    def test_valid_line_item(self):
        """Test creating a valid line item."""
        item = LineItem(
            description="Test Product",
            hsn_code="8471",
            product_code="PROD-001",
            quantity=Decimal("5"),
            unit_of_measure=UnitOfMeasure.PIECE,
            unit_price=Decimal("100.00"),
            tax_rate=Decimal("7.5"),
        )
        assert item.description == "Test Product"
        assert item.quantity == Decimal("5")
        assert item.unit_price == Decimal("100.00")
    
    def test_computed_fields(self):
        """Test computed fields in line item."""
        item = LineItem(
            description="Test Product",
            hsn_code="8471",
            quantity=Decimal("10"),
            unit_of_measure=UnitOfMeasure.PIECE,
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("10"),
            tax_rate=Decimal("7.5"),
        )
        
        # Test computed fields
        assert item.base_amount == Decimal("1000.00")  # 10 * 100
        assert item.discount_amount == Decimal("100.00")  # 10% of 1000
        assert item.taxable_amount == Decimal("900.00")  # 1000 - 100
        assert item.tax_amount == Decimal("67.500")  # 7.5% of 900
        assert item.line_total == Decimal("967.500")  # 900 + 67.5
    
    def test_tax_exemption(self):
        """Test line item with tax exemption."""
        item = LineItem(
            description="Medical Equipment",
            hsn_code="9018",
            quantity=Decimal("2"),
            unit_of_measure=UnitOfMeasure.PIECE,
            unit_price=Decimal("500.00"),
            tax_exemption_reason="Medical equipment - VAT exempt",
        )
        
        assert item.tax_exemption_reason == "Medical equipment - VAT exempt"
        assert item.tax_amount == Decimal("0")
        assert item.line_total == Decimal("1000.00")  # No tax added
    
    def test_invalid_quantity(self):
        """Test line item with invalid quantity."""
        with pytest.raises(ValidationError) as exc_info:
            LineItem(
                description="Invalid Product",
                hsn_code="8471",
                quantity=Decimal("-5"),  # Negative quantity
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
            )
        assert "quantity" in str(exc_info.value).lower()
    
    def test_invalid_tax_rate(self):
        """Test line item with invalid tax rate."""
        with pytest.raises(ValidationError) as exc_info:
            LineItem(
                description="Invalid Tax Product",
                hsn_code="8471",
                quantity=Decimal("1"),
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("150"),  # Over 100%
            )
        assert "tax_rate" in str(exc_info.value).lower()


class TestInvoice:
    """Test Invoice model."""
    
    def test_valid_invoice(self, sample_supplier, sample_customer, sample_payment_details):
        """Test creating a valid invoice."""
        invoice = Invoice(
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            payment_details=sample_payment_details,
            line_items=[],
        )
        
        assert invoice.invoice_number == "INV-001"
        assert invoice.invoice_type == InvoiceType.STANDARD
        assert invoice.invoice_status == InvoiceStatus.DRAFT
    
    def test_invoice_with_line_items(self, sample_supplier, sample_customer):
        """Test invoice with line items."""
        line_items = [
            LineItem(
                description=f"Product {i}",
                hsn_code="8471",
                quantity=Decimal(str(i)),
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("7.5"),
            )
            for i in range(1, 4)
        ]
        
        invoice = Invoice(
            invoice_number="INV-002",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=line_items,
        )
        
        assert len(invoice.line_items) == 3
        assert invoice.line_count == 3
        assert invoice.subtotal == Decimal("600.00")  # (1+2+3) * 100
        assert invoice.total_tax == Decimal("45.000")  # 7.5% of 600
        assert invoice.total_amount == Decimal("645.000")  # 600 + 45
    
    def test_invoice_totals_with_discounts(self, sample_supplier, sample_customer):
        """Test invoice total calculations with discounts."""
        line_items = [
            LineItem(
                description="Discounted Product",
                hsn_code="8471",
                quantity=Decimal("10"),
                unit_of_measure=UnitOfMeasure.PIECE,
                unit_price=Decimal("100.00"),
                discount_percent=Decimal("20"),  # 20% discount
                tax_rate=Decimal("7.5"),
            )
        ]
        
        invoice = Invoice(
            invoice_number="INV-003",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=line_items,
        )
        
        assert invoice.subtotal == Decimal("1000.00")  # 10 * 100
        assert invoice.total_discount == Decimal("200.00")  # 20% of 1000
        assert invoice.total_tax == Decimal("60.000")  # 7.5% of 800
        assert invoice.total_amount == Decimal("860.000")  # 800 + 60
    
    def test_invalid_invoice_number(self, sample_supplier, sample_customer):
        """Test invoice with invalid invoice number."""
        with pytest.raises(ValidationError) as exc_info:
            Invoice(
                invoice_number="",  # Empty invoice number
                invoice_date=datetime.now(),
                invoice_type=InvoiceType.STANDARD,
                supplier=sample_supplier,
                customer=sample_customer,
                line_items=[],
            )
        assert "invoice_number" in str(exc_info.value).lower()
    
    def test_invoice_status_transitions(self, sample_supplier, sample_customer):
        """Test invoice status transitions."""
        invoice = Invoice(
            invoice_number="INV-004",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            invoice_status=InvoiceStatus.DRAFT,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        assert invoice.invoice_status == InvoiceStatus.DRAFT
        
        # Change status
        invoice.invoice_status = InvoiceStatus.SUBMITTED
        assert invoice.invoice_status == InvoiceStatus.SUBMITTED
    
    def test_invoice_currency(self, sample_supplier, sample_customer):
        """Test invoice with different currency."""
        invoice = Invoice(
            invoice_number="INV-005",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            currency=Currency.USD,
            exchange_rate=Decimal("1.25"),
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        assert invoice.currency == Currency.USD
        assert invoice.exchange_rate == Decimal("1.25")