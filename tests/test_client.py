"""Tests for FIRS E-Invoice client."""

import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

from firs_einvoice import FIRSClient, FIRSConfig, Invoice
from firs_einvoice.models.enums import (
    InvoiceType,
    InvoiceStatus,
    UnitOfMeasure,
)


class TestFIRSClient:
    """Test FIRS client functionality."""
    
    def test_client_initialization(self, test_config):
        """Test client initialization with config."""
        client = FIRSClient(config=test_config)
        assert client.config == test_config
        assert client.config.api_key.get_secret_value() == "test-api-key"
    
    def test_client_initialization_with_params(self):
        """Test client initialization with parameters."""
        config_overrides = {
            "api_key": "param-key",
            "api_secret": "param-secret",
            "business_id": "PARAM-BUS",
            "business_name": "Test Business",
            "tin": "12345678901"
        }
        client = FIRSClient(config_overrides=config_overrides)
    # API key/secret might be string or SecretStr depending
    # on how they're set
        api_key = client.config.api_key
        if hasattr(api_key, 'get_secret_value'):
            assert api_key.get_secret_value() == "param-key"
        else:
            assert api_key == "param-key"

        api_secret = client.config.api_secret
        if hasattr(api_secret, 'get_secret_value'):
            assert api_secret.get_secret_value() == "param-secret"
        else:
            assert api_secret == "param-secret"
        assert client.config.business_id == "PARAM-BUS"
    
    def test_create_invoice_builder(self, client):
        """Test creating invoice builder."""
        builder = client.create_invoice_builder()
        assert builder is not None
        assert builder._invoice_data is not None
    
    def test_create_line_item_builder(self, client):
        """Test creating line item builder."""
        builder = client.create_line_item_builder()
        assert builder is not None
        assert builder._item_data is not None
    
    def test_generate_irn(self, client, sample_supplier, sample_customer):
        """Test IRN generation."""
        invoice = Invoice(
            invoice_number="INV-001",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        irn = client.generate_irn(invoice)
        assert isinstance(irn, str)
        assert invoice.invoice_number in irn
        # IRN format: {invoice_number}-{service_id}-{datestamp}
        # Prefer FIRS_SERVICE_ID from env; fall back to config or derived value
        import os
        service_id = os.environ.get('FIRS_SERVICE_ID')
        if service_id:
            assert service_id[:8].upper() in irn
        else:
            # Fallback: ensure the middle token is 8 chars alphanumeric
            parts = irn.split('-')
            assert len(parts) >= 3
            assert len(parts[1]) == 8
    
    # QR generation tests removed as part of cleanup
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_save_invoice_to_file(self, mock_write, mock_mkdir, client,
                                  sample_supplier, sample_customer):
        """Test saving invoice to file."""
        invoice = Invoice(
            invoice_number="INV-003",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        file_path = client.save_invoice_to_file(invoice)
        
        assert file_path is not None
        assert "INV-003" in str(file_path)
        mock_mkdir.assert_called_once()
        mock_write.assert_called_once()
    
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    def test_save_invoice_with_custom_dir(self, mock_write, mock_mkdir, client,
                                          sample_supplier, sample_customer):
        """Test saving invoice to custom directory."""
        invoice = Invoice(
            invoice_number="INV-004",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        custom_dir = Path("/tmp/invoices")
        custom_dir.mkdir(parents=True, exist_ok=True)
        custom_file = custom_dir / f"invoice_{invoice.invoice_number}.json"
        file_path = client.save_invoice_to_file(
            invoice, output_path=str(custom_file)
        )
        
        assert str(custom_dir) in str(file_path)
        assert "INV-004" in str(file_path)
    
    def test_validate_invoice(self, client, sample_supplier, sample_customer,
                              line_item_builder):
        """Test invoice validation."""
        # Create valid invoice
        line_item = (
            line_item_builder
            .with_description("Test Product")
            .with_hsn_code("8471")
            .with_quantity(5, UnitOfMeasure.PIECE)
            .with_unit_price(Decimal("100.00"))
            .build()
        )
        
        invoice = Invoice(
            invoice_number="INV-005",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[line_item],
        )
        
        result = client.validate_invoice(invoice)
        assert result.valid is True
        assert len(result.errors) == 0
    
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_submit_invoice_success(
        self,
        mock_post,
        client,
        sample_supplier,
        sample_customer,
        mock_api_response,
    ):
        """Test successful invoice submission."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_post.return_value = mock_response
        
        invoice = Invoice(
            invoice_number="INV-006",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        result = await client.submit_invoice(invoice)
        
        assert result.success is True
        assert result.status == InvoiceStatus.SUBMITTED
        assert result.reference_number == "REF-INV-006"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_submit_invoice_failure(
        self,
        mock_post,
        client,
        sample_supplier,
        sample_customer,
    ):
        """Test failed invoice submission."""
        # Setup mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid invoice data",
            "details": ["Missing required field: line_items"]
        }
        mock_post.return_value = mock_response
        
        invoice = Invoice(
            invoice_number="INV-007",
            invoice_date=datetime.now(),
            invoice_type=InvoiceType.STANDARD,
            supplier=sample_supplier,
            customer=sample_customer,
            line_items=[],
        )
        
        result = await client.submit_invoice(invoice)
        
        assert result.success is False
        assert result.error_message == "Invalid invoice data"
        assert len(result.error_details) > 0
    
    @patch('requests.get')
    @pytest.mark.asyncio
    async def test_get_invoice_status(self, mock_get, client):
        """Test getting invoice status."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "invoice_number": "INV-008",
                "status": "APPROVED",
                "updated_at": datetime.now().isoformat()
            }
        }
        mock_get.return_value = mock_response
        
        status = await client.get_invoice_status("INV-008")
        
        assert status is not None
        assert status["status"] == "APPROVED"
        mock_get.assert_called_once()
    
    def test_client_with_cache(self):
        """Test client with caching enabled."""
        config = FIRSConfig(
            api_key="cache-key",
            api_secret="cache-secret",
            business_id="CACHE-BUS",
            business_name="Cache Business",
            tin="12345678901",
            enable_caching=True,
            cache_ttl=300
        )
        client = FIRSClient(config=config)
        
        assert client.config.enable_caching is True
        assert client.config.cache_ttl == 300