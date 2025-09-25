"""Example demonstrating local and remote invoice validation."""

import asyncio
from zutax import ZutaxClient, ZutaxConfig
from zutax.models.invoice import Invoice
from zutax.models.party import Party, Address
from zutax.models.line_item import LineItem
from decimal import Decimal


async def main():
    # Initialize client with config
    config = ZutaxConfig(
        api_key="test_key",
        api_secret="test_secret",
        business_id="BUS001",
        business_name="Test Business",
        tin="12345678901"
    )
    client = ZutaxClient(config=config)
    
    # Create a test invoice
    from datetime import datetime
    invoice = Invoice(
        invoice_number="INV-TEST-001",
        invoice_date=datetime.now(),
        supplier=Party(
            business_id="SUP001",
            tin="12345678901",
            name="Test Supplier",
            email="supplier@test.com",
            phone="+2348012345678",
            address=Address(
                street="123 Test St",
                city="Lagos",
                state_code="LA",
                country_code="NG"
            )
        ),
        customer=Party(
            business_id="CUS001",
            tin="98765432101",
            name="Test Customer",
            email="customer@test.com", 
            phone="+2348087654321",
            address=Address(
                street="456 Customer Ave",
                city="Abuja",
                state_code="FC",
                country_code="NG"
            )
        ),
        line_items=[
            LineItem(
                description="Test Product",
                hsn_code="8471",
                quantity=Decimal("10"),
                unit_price=Decimal("100.00"),
                tax_rate=Decimal("7.5")
            )
        ]
    )
    
    print("Testing Invoice Validation")
    print("=" * 50)
    
    # 1. Local validation only (synchronous)
    print("\n1. Local validation (sync):")
    local_result = client.validate_invoice(invoice)
    print(f"   Valid: {local_result.valid}")
    if local_result.errors:
        print(f"   Errors: {local_result.errors}")
    
    # 2. Local + Remote validation (async)
    print("\n2. Local + Remote validation (async):")
    try:
        remote_result = await client.validate_invoice_async(invoice, remote=True)
        print(f"   Valid: {remote_result.valid}")
        if remote_result.errors:
            print(f"   Errors: {remote_result.errors}")
        if remote_result.warnings:
            print(f"   Warnings: {remote_result.warnings}")
    except Exception as e:
        print(f"   Remote validation failed: {e}")
    
    # 3. Test with invalid invoice
    print("\n3. Testing with invalid invoice:")
    try:
        # This will fail during construction due to validation
        invalid_invoice = Invoice(
            invoice_number="I",  # Too short
            invoice_date=datetime.now(),
            supplier=invoice.supplier,
            customer=invoice.customer,
            line_items=invoice.line_items
        )
    except Exception as e:
        print(f"   Construction failed (as expected): {e}")
        print("   This shows Pydantic validation working at model level")


if __name__ == "__main__":
    asyncio.run(main())