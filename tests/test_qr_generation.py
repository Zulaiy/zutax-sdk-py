"""Tests for QR code generation and file output."""

import pytest
import json
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch, Mock

from firs_einvoice import FIRSClient, Invoice, LineItem
from firs_einvoice.models.enums import InvoiceType, UnitOfMeasure


class TestQRCodeGeneration:
    """Test QR code generation functionality."""
    
    def test_generate_qr_code_data(self, client, sample_supplier, sample_customer, 
                                  line_item_builder):
        """Test QR code data generation with complete invoice."""
        # Create line items
        item1 = (line_item_builder
                .with_description("Laptop Computer")
                .with_hsn_code("8471")
                .with_product_code("LAP-001")
                .with_quantity(2, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("150000.00"))
                .with_discount_percent(Decimal("5"))
                .with_tax(Decimal("7.5"))
                .build())
        
        line_item_builder.reset()
        item2 = (line_item_builder
                .with_description("Software License")
                .with_hsn_code("9984")
                .with_product_code("SW-001")
                .with_quantity(5, UnitOfMeasure.UNIT)
                .with_unit_price(Decimal("20000.00"))
                .with_tax(Decimal("7.5"))
                .build())
        
        # Create invoice with IRN
        invoice = Invoice(
            invoice_number="INV-QR-001",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[item1, item2],
            irn="INV-QR-001-TEST-BUS-20240816"
        )
        
        # Generate QR code data
        qr_data = client.generate_qr_code_data(invoice)
        
        # Verify QR data is valid JSON
        assert qr_data is not None
        data = json.loads(qr_data)
        
        # Verify required fields
        assert data["irn"] == "INV-QR-001-TEST-BUS-20240816"
        assert data["invoice_number"] == "INV-QR-001"
        assert "total" in data
        assert "date" in data
        assert "supplier" in data
        assert "customer" in data
        
        # Verify total amount
        expected_total = invoice.total_amount
        assert Decimal(data["total"]) == expected_total
    
    @patch('qrcode.QRCode')
    @pytest.mark.asyncio
    async def test_generate_qr_code_to_file(self, mock_qr_class, client, sample_supplier, 
                                     sample_customer):
        """Test generating QR code to file."""
        # Setup mock QR code
        mock_qr = Mock()
        mock_img = Mock()
        mock_qr.make_image.return_value = mock_img
        mock_qr_class.return_value = mock_qr
        
        # Create simple invoice
        invoice = Invoice(
            invoice_number="INV-QR-002",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
            irn="INV-QR-002-TEST-BUS-20240816"
        )
        
        # Generate QR code to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir)
            
            file_path = await client.generate_qr_code_to_file(invoice, output_dir=str(output_path))
            
            # Verify file path
            assert file_path is not None
            assert "INV-QR-002" in str(file_path)
            assert str(output_path) in str(file_path)
            assert Path(file_path).suffix == ".png"
            
            # Verify QR code was created (placeholder implementation just writes text)
            # The actual QR generation would use the mocked QR code
    
    def test_qr_code_integration_test(self, client, sample_supplier, sample_customer,
                                     line_item_builder):
        """Integration test for complete QR code workflow."""
        # Create comprehensive invoice
        items = []
        
        # Standard VAT item
        item1 = (line_item_builder
                .with_description("Office Chair")
                .with_hsn_code("9401")
                .with_product_code("CHAIR-001")
                .with_quantity(3, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("25000.00"))
                .with_discount_percent(Decimal("10"))
                .with_tax(Decimal("7.5"))
                .build())
        items.append(item1)
        
        # VAT exempt item
        line_item_builder.reset()
        item2 = (line_item_builder
                .with_description("Medical Equipment")
                .with_hsn_code("9018")
                .with_product_code("MED-001")
                .with_quantity(1, UnitOfMeasure.PIECE)
                .with_unit_price(Decimal("50000.00"))
                .with_tax_exemption("Medical equipment - VAT exempt")
                .build())
        items.append(item2)
        
        # Create invoice
        invoice = Invoice(
            invoice_number="INV-QR-INTEGRATION",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=items,
            reference_number="PO-2024-QR-001",
            notes="Test invoice for QR code generation",
        )
        
        # Generate IRN
        irn = client.generate_irn(invoice)
        invoice.irn = irn
        
        # Generate QR code data
        qr_data = client.generate_qr_code_data(invoice)
        data = json.loads(qr_data)
        
        # Verify comprehensive data
        assert data["irn"] == irn
        assert data["invoice_number"] == "INV-QR-INTEGRATION"
        assert data["supplier"] == sample_supplier.name
        assert data["customer"] == sample_customer.name
        
        # Verify calculated totals
        expected_subtotal = Decimal("125000.00")  # 75000 + 50000
        expected_discount = Decimal("7500.00")    # 10% of 75000
        expected_tax = Decimal("5062.500")        # 7.5% of 67500 (only chair is taxable)
        expected_total = Decimal("122562.500")    # 117500 + 5062.5
        
        assert invoice.subtotal == expected_subtotal
        assert invoice.total_discount == expected_discount
        assert invoice.total_tax == expected_tax
        assert invoice.total_amount == expected_total
        assert Decimal(data["total"]) == expected_total
    
    @pytest.mark.asyncio
    async def test_qr_code_output_to_custom_folder(self, client, sample_supplier, 
                                           sample_customer):
        """Test QR code generation to custom output folder."""
        # Create invoice
        invoice = Invoice(
            invoice_number="INV-QR-CUSTOM",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
            irn="INV-QR-CUSTOM-TEST-BUS-20240816"
        )
        
        # Create custom output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "qr_codes" / "test_invoices"
            
            # Generate QR code (this will create the directory)
            with patch('qrcode.QRCode') as mock_qr_class:
                mock_qr = Mock()
                mock_img = Mock()
                mock_qr.make_image.return_value = mock_img
                mock_qr_class.return_value = mock_qr
                
                file_path = await client.generate_qr_code_to_file(invoice, output_dir=str(custom_dir))
                
                # Verify directory structure was created
                assert custom_dir.exists()
                assert str(custom_dir) in str(file_path)
                assert "INV-QR-CUSTOM" in str(file_path)
    
    def test_qr_code_data_structure(self, client, sample_supplier, sample_customer):
        """Test QR code data contains all required fields."""
        invoice = Invoice(
            invoice_number="INV-QR-STRUCTURE",
            invoice_date=datetime(2024, 8, 16, 10, 30, 0),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
            irn="INV-QR-STRUCTURE-TEST-BUS-20240816"
        )
        
        qr_data = client.generate_qr_code_data(invoice)
        data = json.loads(qr_data)
        
        # Verify all required fields are present
        required_fields = ["irn", "invoice_number", "total", "date", "supplier", "customer"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify data types and formats
        assert isinstance(data["irn"], str)
        assert isinstance(data["invoice_number"], str)
        assert isinstance(data["total"], str)  # Should be string for precise decimal handling
        assert isinstance(data["date"], str)
        assert isinstance(data["supplier"], str)
        assert isinstance(data["customer"], str)
        
        # Verify date format (ISO format)
        assert "2024-08-16T10:30:00" in data["date"]
    
    @patch('pathlib.Path.mkdir')
    @patch('qrcode.QRCode')
    @pytest.mark.asyncio
    async def test_qr_code_file_naming(self, mock_qr_class, mock_mkdir, client, 
                                sample_supplier, sample_customer):
        """Test QR code file naming convention."""
        # Setup mocks
        mock_qr = Mock()
        mock_img = Mock()
        mock_qr.make_image.return_value = mock_img
        mock_qr_class.return_value = mock_qr
        
        invoice = Invoice(
            invoice_number="INV/2024/001",  # Test with special characters
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
            irn="INV-2024-001-TEST-BUS-20240816"
        )
        
        file_path = await client.generate_qr_code_to_file(invoice)
        
        # Verify file naming (special characters should be replaced)
        assert "INV_2024_001" in str(file_path)  # Slashes replaced with underscores
        assert Path(file_path).suffix == ".png"
        assert "qr" in str(file_path).lower()
    
    def test_multiple_qr_codes_generation(self, client, sample_supplier, 
                                         sample_customer, line_item_builder):
        """Test generating multiple QR codes for different invoices."""
        invoices = []
        
        # Create multiple invoices
        for i in range(3):
            item = (line_item_builder
                   .with_description(f"Product {i+1}")
                   .with_hsn_code("8471")
                   .with_quantity(i+1, UnitOfMeasure.PIECE)
                   .with_unit_price(Decimal("1000.00"))
                   .with_tax(Decimal("7.5"))  # 7.5% tax rate
                   .build())
            line_item_builder.reset()
            
            invoice = Invoice(
                invoice_number=f"INV-MULTI-{i+1:03d}",
                invoice_date=datetime.now(),
                invoice_type=InvoiceType.STANDARD,
                supplier=sample_supplier,
                customer=sample_customer,
                line_items=[item],
                irn=f"INV-MULTI-{i+1:03d}-TEST-BUS-20240816"
            )
            invoices.append(invoice)
        
        # Generate QR codes for all invoices
        qr_data_list = []
        for invoice in invoices:
            qr_data = client.generate_qr_code_data(invoice)
            qr_data_list.append(json.loads(qr_data))
        
        # Verify each QR code has unique data
        invoice_numbers = [data["invoice_number"] for data in qr_data_list]
        assert len(set(invoice_numbers)) == 3  # All unique
        
        # Verify totals are different (based on quantity with 7.5% tax)
        totals = [Decimal(data["total"]) for data in qr_data_list]
        assert totals[0] == Decimal("1075.000")  # 1 * 1000 + 7.5% tax = 1075
        assert totals[1] == Decimal("2150.000")  # 2 * 1000 + 7.5% tax = 2150
        assert totals[2] == Decimal("3225.000")  # 3 * 1000 + 7.5% tax = 3225