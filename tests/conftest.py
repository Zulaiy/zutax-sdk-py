"""Pytest configuration and fixtures for FIRS E-Invoice tests."""

import pytest
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any

from zutax import (
    ZutaxClient as FIRSClient,
    ZutaxConfig as FIRSConfig,
    InvoiceBuilder,
    LineItemBuilder,
    Party,
    Address,
    PaymentDetails,
    PaymentMethod,
    InvoiceType,
    InvoiceStatus,
)
from zutax.models.enums import (
    Currency,
    UnitOfMeasure,
    TaxCategory,
    CountryCode,
)


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return FIRSConfig(
        api_key="test-api-key",
        api_secret="test-api-secret",
        business_id="TEST-BUS-001",
        business_name="Test Business Ltd",
        tin="12345678",
        base_url="https://api-sandbox.firs.gov.ng",
    )


@pytest.fixture
def client(test_config):
    """Provide test FIRS client."""
    return FIRSClient(config=test_config)


@pytest.fixture
def sample_address():
    """Provide sample address."""
    from zutax.models.enums import StateCode
    return Address(
        street="123 Test Street",
        city="Lagos",
        state_code=StateCode.LA,
        postal_code="100001",
        country_code=CountryCode.NG,
    )


@pytest.fixture
def sample_supplier(sample_address):
    """Provide sample supplier party."""
    return Party(
        business_id="SUP-001",
        tin="12345678901",
        name="Test Supplier Ltd",
        trade_name="TestSup",
        email="supplier@test.com",
        phone="+2348012345678",
        address=sample_address,
    )


@pytest.fixture
def sample_customer(sample_address):
    """Provide sample customer party."""
    return Party(
        business_id="CUS-001",
        tin="98765432101",
        name="Test Customer Ltd",
        trade_name="TestCust",
        email="customer@test.com",
        phone="+2348087654321",
        address=sample_address,
    )


@pytest.fixture
def sample_payment_details():
    """Provide sample payment details."""
    return PaymentDetails(
        method=PaymentMethod.BANK_TRANSFER,
        bank_name="Test Bank",
        account_number="1234567890",
        account_name="Test Supplier Ltd",
        reference="PAY-001",
    )


@pytest.fixture
def invoice_builder(client):
    """Provide invoice builder."""
    return client.create_invoice_builder()


@pytest.fixture
def line_item_builder(client):
    """Provide line item builder."""
    return client.create_line_item_builder()


@pytest.fixture
def sample_line_item_data():
    """Provide sample line item data."""
    return {
        "description": "Test Product",
        "hsn_code": "8471",
        "product_code": "PROD-001",
        "quantity": Decimal("10"),
        "unit_of_measure": UnitOfMeasure.PIECE,
        "unit_price": Decimal("1000.00"),
        "tax_rate": Decimal("7.5"),
        "tax_category": TaxCategory.VAT,
    }


@pytest.fixture
def sample_invoice_data(sample_supplier, sample_customer, sample_payment_details):
    """Provide sample invoice data."""
    return {
        "invoice_number": "INV-TEST-001",
        "invoice_type": InvoiceType.STANDARD,
        "invoice_date": datetime.now(),
        "supplier": sample_supplier,
        "customer": sample_customer,
        "payment_details": sample_payment_details,
        "reference_number": "REF-001",
        "notes": "Test invoice",
        "terms_and_conditions": "Test terms",
    }


@pytest.fixture
def mock_api_response():
    """Provide mock API response for testing."""
    return {
        "success": True,
        "data": {
            "invoice_id": "FIRS-INV-001",
            "status": "SUBMITTED",
            "submission_date": datetime.now().isoformat(),
            "reference_number": "REF-001",
        },
        "message": "Invoice submitted successfully",
    }