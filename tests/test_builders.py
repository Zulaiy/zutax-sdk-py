"""Tests for FIRS E-Invoice builders."""

import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from firs_einvoice import (
    InvoiceBuilder,
    LineItemBuilder,
    Invoice,
    LineItem,
)
from firs_einvoice.models.enums import (
    InvoiceType,
    InvoiceStatus,
    UnitOfMeasure,
    TaxCategory,
)


class TestLineItemBuilder:
    """Test LineItemBuilder class."""
    
    def test_build_basic_line_item(self, line_item_builder):
        """Test building a basic line item."""
        item = (line_item_builder
                .with_description("Test Product")
                .with_hsn_code("8471")
                .with_quantity(5, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("100.00"))
                .build())
        
        assert isinstance(item, LineItem)
        assert item.description == "Test Product"
        assert item.hsn_code == "8471"
        assert item.quantity == 5
        assert item.unit_price == Decimal("100.00")
    
    def test_build_line_item_with_tax(self, line_item_builder):
        """Test building line item with tax."""
        item = (line_item_builder
                .with_description("Taxable Product")
                .with_hsn_code("8471")
                .with_quantity(10, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("50.00"))
                .with_tax(Decimal("7.5"), TaxCategory.VAT)
                .build())
        
        assert item.tax_rate == Decimal("7.5")
        assert item.tax_category == TaxCategory.VAT
        assert item.tax_amount == Decimal("37.500")  # 7.5% of 500
    
    def test_build_line_item_with_discount(self, line_item_builder):
        """Test building line item with discount."""
        item = (line_item_builder
                .with_description("Discounted Product")
                .with_hsn_code("8471")
                .with_quantity(2, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("200.00"))
                .with_discount_percent(Decimal("15"))
                .build())
        
        assert item.discount_percent == Decimal("15")
        assert item.discount_amount == Decimal("60.00")  # 15% of 400
        assert item.taxable_amount == Decimal("340.00")  # 400 - 60
    
    def test_build_line_item_with_exemption(self, line_item_builder):
        """Test building tax-exempt line item."""
        item = (line_item_builder
                .with_description("Medical Equipment")
                .with_hsn_code("9018")
                .with_quantity(1, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("1000.00"))
                .with_tax_exemption("Medical equipment - VAT exempt")
                .build())
        
        assert item.tax_exemption_reason == "Medical equipment - VAT exempt"
        assert item.tax_amount == Decimal("0")
        assert item.line_total == Decimal("1000.00")
    
    def test_builder_reset(self, line_item_builder):
        """Test resetting the builder."""
        # Build first item
        item1 = (line_item_builder
                .with_description("First Product")
                .with_hsn_code("8471")
                .with_quantity(5, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("100.00"))
                .build())
        
        # Reset and build second item
        line_item_builder.reset()
        item2 = (line_item_builder
                .with_description("Second Product")
                .with_hsn_code("9984")
                .with_quantity(10, UnitOfMeasure.UNIT)
                .with_unit_price(Decimal("50.00"))
                .build())
        
        assert item1.description == "First Product"
        assert item2.description == "Second Product"
        assert item1.hsn_code == "8471"
        assert item2.hsn_code == "9984"
    
    def test_build_without_required_fields(self, line_item_builder):
        """Test building without required fields raises error."""
        with pytest.raises(ValueError) as exc_info:
            line_item_builder.build()
        assert "description is required" in str(exc_info.value)
    
    def test_build_with_all_fields(self, line_item_builder):
        """Test building with all available fields."""
        item = (line_item_builder
                .with_description("Complete Product")
                .with_hsn_code("8471")
                .with_product_code("PROD-001")
                .with_batch_number("BATCH-2024-01")
                .with_serial_number("SN123456")
                .with_quantity(3, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("150.00"))
                .with_discount_percent(Decimal("10"))
                .with_charge(Decimal("5.00"), "Handling fee")
                .with_tax(Decimal("7.5"), TaxCategory.VAT)
                .with_notes("Special instructions")
                .build())
        
        assert item.product_code == "PROD-001"
        assert item.batch_number == "BATCH-2024-01"
        assert item.serial_number == "SN123456"
        assert item.notes == "Special instructions"
        assert item.charge_amount == Decimal("5.00")


class TestInvoiceBuilder:
    """Test InvoiceBuilder class."""
    
    def test_build_basic_invoice(self, invoice_builder, sample_supplier, sample_customer):
        """Test building a basic invoice."""
        invoice = (invoice_builder
                  .with_invoice_number("INV-001")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .build())
        
        assert isinstance(invoice, Invoice)
        assert invoice.invoice_number == "INV-001"
        assert invoice.invoice_type == InvoiceType.STANDARD
        assert invoice.supplier == sample_supplier
        assert invoice.customer == sample_customer
    
    def test_build_invoice_with_line_items(self, invoice_builder, sample_supplier, 
                                          sample_customer, line_item_builder):
        """Test building invoice with line items."""
        # Create line items
        item1 = (line_item_builder
                .with_description("Product 1")
                .with_hsn_code("8471")
                .with_quantity(2, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("100.00"))
                .build())
        
        line_item_builder.reset()
        item2 = (line_item_builder
                .with_description("Product 2")
                .with_hsn_code("9984")
                .with_quantity(3, UnitOfMeasure.UNIT)
                .with_unit_price(Decimal("50.00"))
                .build())
        
        # Build invoice with items
        invoice = (invoice_builder
                  .with_invoice_number("INV-002")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .add_line_item(item1)
                  .add_line_item(item2)
                  .build())
        
        assert len(invoice.line_items) == 2
        assert invoice.line_count == 2
        assert invoice.subtotal == Decimal("350.00")  # 200 + 150
    
    def test_build_invoice_with_payment_details(self, invoice_builder, sample_supplier,
                                                sample_customer, sample_payment_details):
        """Test building invoice with payment details."""
        invoice = (invoice_builder
                  .with_invoice_number("INV-003")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .with_payment_details(sample_payment_details)
                  .build())
        
        assert invoice.payment_details == sample_payment_details
        assert invoice.payment_details.method == sample_payment_details.method
    
    def test_build_invoice_with_dates(self, invoice_builder, sample_supplier, sample_customer):
        """Test building invoice with custom dates."""
        invoice_date = datetime(2024, 1, 15, 10, 30)
        due_date = datetime(2024, 2, 15)
        
        invoice = (invoice_builder
                  .with_invoice_number("INV-004")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_invoice_date(invoice_date)
                  .with_due_date(due_date)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .build())
        
        assert invoice.invoice_date == invoice_date
        assert invoice.due_date == due_date.date()
    
    def test_build_invoice_with_reference(self, invoice_builder, sample_supplier, sample_customer):
        """Test building invoice with reference numbers."""
        invoice = (invoice_builder
                  .with_invoice_number("INV-005")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_reference_number("PO-2024-001")
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .build())
        
        assert invoice.reference_number == "PO-2024-001"
    
    def test_build_invoice_with_notes(self, invoice_builder, sample_supplier, sample_customer):
        """Test building invoice with notes and terms."""
        notes = "Thank you for your business"
        terms = "Payment due within 30 days"
        
        invoice = (invoice_builder
                  .with_invoice_number("INV-006")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .with_notes(notes)
                  .with_terms_and_conditions(terms)
                  .build())
        
        assert invoice.notes == notes
        assert invoice.terms_and_conditions == terms
    
    def test_build_credit_note(self, invoice_builder, sample_supplier, sample_customer):
        """Test building a credit note."""
        invoice = (invoice_builder
                  .with_invoice_number("CN-001")
                  .with_invoice_type(InvoiceType.CREDIT)
                  .with_original_invoice_number("INV-001")
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .build())
        
        assert invoice.invoice_type == InvoiceType.CREDIT
        assert invoice.original_invoice_number == "INV-001"
    
    def test_build_without_required_fields(self, invoice_builder):
        """Test building without required fields raises error."""
        with pytest.raises(ValueError) as exc_info:
            invoice_builder.build()
        assert "required" in str(exc_info.value).lower()
    
    def test_builder_validation(self, invoice_builder, sample_supplier, sample_customer):
        """Test builder validation catches errors."""
        # Try to build with empty invoice number
        invoice_builder.with_invoice_number("")
        invoice_builder.with_supplier(sample_supplier)
        invoice_builder.with_customer(sample_customer)
        
        with pytest.raises(ValueError):
            invoice_builder.build()
    
    def test_build_invoice_different_parties(self, invoice_builder, sample_supplier,
                                            sample_customer, sample_address):
        """Test building invoice with billing and shipping parties."""
        from firs_einvoice import Party
        
        billing_party = Party(
            business_id="BILL-001",
            tin="11111111111",
            name="Billing Company",
            email="billing@test.com",
            phone="+2348011111111",
            address=sample_address,
        )
        
        shipping_party = Party(
            business_id="SHIP-001",
            tin="22222222222",
            name="Shipping Company",
            email="shipping@test.com",
            phone="+2348022222222",
            address=sample_address,
        )
        
        invoice = (invoice_builder
                  .with_invoice_number("INV-007")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(sample_supplier)
                  .with_customer(sample_customer)
                  .with_billing_party(billing_party)
                  .with_shipping_party(shipping_party)
                  .build())
        
        assert invoice.billing_party == billing_party
        assert invoice.shipping_party == shipping_party