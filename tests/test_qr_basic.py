#!/usr/bin/env python3
"""Simple QR code generation test that outputs to a folder."""

import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Import the SDK
from firs_einvoice import FIRSClient, FIRSConfig
from firs_einvoice.models.invoice import Invoice
from firs_einvoice.models.party import Party, Address
from firs_einvoice.models.line_item import LineItem, Discount
from firs_einvoice.models.enums import (
    InvoiceType, 
    StateCode, 
    CountryCode, 
    UnitOfMeasure,
    TaxCategory
)


async def main():
    """Generate QR codes and save to output folder."""
    
    print("🔗 FIRS E-Invoice QR Code Generation Test")
    print("=" * 50)
    
    # 1. Setup client
    config = FIRSConfig(
        api_key="test-key",
        api_secret="test-secret", 
        business_id="TEST-BUS-001",
        environment="sandbox"
    )
    client = FIRSClient(config=config)
    print("✓ Client initialized")
    
    # 2. Create address
    address = Address(
        street="123 Test Street",
        city="Lagos",
        state_code=StateCode.LA,
        postal_code="100001",
        country_code=CountryCode.NG
    )
    
    # 3. Create parties
    supplier = Party(
        business_id="SUP-001",
        tin="12345678901",
        name="Test Supplier Ltd",
        email="supplier@test.com",
        phone="+2348012345678",
        address=address
    )
    
    customer = Party(
        business_id="CUS-001", 
        tin="98765432101",
        name="Test Customer Ltd",
        email="customer@test.com",
        phone="+2348087654321",
        address=address
    )
    print("✓ Parties created")
    
    # 4. Create line item
    line_item = LineItem(
        description="Test Product - Laptop Computer",
        hsn_code="8471",
        product_code="LAP-001",
        quantity=Decimal("2"),
        unit_of_measure=UnitOfMeasure.PIECE,
        unit_price=Decimal("150000.00"),
        discount=Discount(percent=Decimal("10")),
        tax_rate=Decimal("7.5")
    )
    print("✓ Line item created")
    
    # 5. Create invoice
    invoice = Invoice(
        invoice_number="QR-TEST-001",
        invoice_date=datetime.now(),
        invoice_type=InvoiceType.STANDARD,
        supplier=supplier,
        customer=customer,
        line_items=[line_item]
    )
    print("✓ Invoice created")
    
    # 6. Generate IRN
    irn = client.generate_irn(invoice)
    invoice.irn = irn
    print(f"✓ IRN generated: {irn}")
    
    # 7. Create output directory
    output_dir = Path("qr_output")
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory: {output_dir.absolute()}")
    
    # 8. Generate QR code data
    qr_data = await client.generate_qr_code(invoice)
    print("✓ QR code data generated")
    
    # 9. Save QR data to JSON file
    qr_file = output_dir / f"qr_data_{invoice.invoice_number}.json"
    with open(qr_file, 'w') as f:
        json.dump(json.loads(qr_data), f, indent=2)
    print(f"✓ QR data saved to: {qr_file}")
    
    # 10. Generate QR code image
    try:
        qr_image_file = await client.generate_qr_code_to_file(invoice, output_dir=output_dir)
        print(f"✓ QR image saved to: {qr_image_file}")
    except Exception as e:
        print(f"⚠ QR image generation failed (needs qrcode library): {e}")
    
    # 11. Display summary
    print("\n📊 Invoice Summary:")
    print(f"   Invoice Number: {invoice.invoice_number}")
    print(f"   Subtotal: ₦{invoice.subtotal:,.2f}")
    print(f"   Total Tax: ₦{invoice.total_tax:,.2f}")
    print(f"   Total Amount: ₦{invoice.total_amount:,.2f}")
    
    print(f"\n📁 Files generated in {output_dir.absolute()}:")
    for file in output_dir.glob("*"):
        print(f"   - {file.name}")
    
    print("\n✅ QR code generation test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())