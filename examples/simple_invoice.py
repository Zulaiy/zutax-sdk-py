#!/usr/bin/env python3
"""
Simple invoice creation example using FIRS E-Invoice Python SDK with Pydantic.

This example demonstrates:
- Creating parties (supplier and customer)
- Building an invoice with line items
- Validating the invoice
- Generating IRN and QR code
"""

import os
import asyncio
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from the package
from firs_einvoice import (
    FIRSClient,
    FIRSConfig,
    InvoiceBuilder,
    LineItemBuilder,
    Party,
    Address,
    PaymentDetails,
    InvoiceType,
    PaymentMethod,
)
from firs_einvoice.models.enums import StateCode, UnitOfMeasure


def create_supplier() -> Party:
    """Create supplier/seller party with Pydantic validation."""
    return Party(
        business_id="SUP-001",
        tin="12345678901",
        name="Tech Solutions Nigeria Ltd",
        trade_name="TechSol",
        email="info@techsol.ng",
        phone="08012345678",
        address=Address(
            street="123 Victoria Island",
            street2="Suite 45",
            city="Lagos",
            state_code=StateCode.LA,
            lga_code="ETI-OSA",
            postal_code="101241",
        ),
        vat_registered=True,
        vat_number="VAT123456",
        registration_number="RC123456",
    )


def create_customer() -> Party:
    """Create customer/buyer party with Pydantic validation."""
    return Party(
        business_id="CUS-001",
        tin="87654321901",
        name="Global Enterprises Limited",
        email="purchasing@globalent.ng",
        phone="08087654321",
        address=Address(
            street="456 Maitama District",
            city="Abuja",
            state_code=StateCode.FC,
            lga_code="ABUJA-MUNICIPAL",
            postal_code="900271",
        ),
        vat_registered=True,
        vat_number="VAT654321",
    )


def create_payment_details() -> PaymentDetails:
    """Create payment details."""
    from datetime import date, timedelta
    
    return PaymentDetails(
        method=PaymentMethod.BANK_TRANSFER,
        terms="Net 30",
        due_date=date.today() + timedelta(days=30),
        bank_name="First Bank of Nigeria",
        account_number="1234567890",
        account_name="Tech Solutions Nigeria Ltd",
        reference="INV-2024-001-PAY",
    )


async def main():
    """Main function demonstrating invoice creation and processing."""
    
    print("=" * 60)
    print("FIRS E-Invoice Python SDK - Simple Invoice Example")
    print("Using Pydantic v2 for Data Validation")
    print("=" * 60)
    
    # 1. Initialize the client
    print("\n1. Initializing FIRS Client...")
    
    # Create FIRSConfig object
    config = FIRSConfig(
        api_key=os.environ.get('FIRS_API_KEY', 'demo_api_key'),
        api_secret=os.environ.get('FIRS_API_SECRET', 'demo_api_secret'),
        business_id=os.environ.get('BUSINESS_ID', 'DEMO-BUS-001'),
        business_name=os.environ.get('BUSINESS_NAME', 'Demo Business Ltd'),
        tin=os.environ.get('TIN', '12345678901'),  # Fixed to match regex
        service_id=os.environ.get('FIRS_SERVICE_ID', '94ND90NR')
    )
    
    # Initialize client with config
    client = FIRSClient(config=config)
    print("   ✓ Client initialized")
    
    # 2. Create parties
    print("\n2. Creating Parties...")
    supplier = create_supplier()
    customer = create_customer()
    print(f"   ✓ Supplier: {supplier.name}")
    print(f"   ✓ Customer: {customer.name}")
    
    # 3. Start building invoice using the fluent builder
    print("\n3. Building Invoice...")
    invoice_builder = client.create_invoice_builder()
    
    invoice_builder = (invoice_builder
        .with_invoice_number("INV-2024-001")
        .with_invoice_type(InvoiceType.STANDARD)
        .with_invoice_date(datetime.now())
        .with_supplier(supplier)
        .with_customer(customer)
        .with_reference_number("PO-2024-789")
        .with_payment_details(create_payment_details())
        .with_notes("Thank you for your business!")
        .with_terms_and_conditions("Payment due within 30 days. Late payments subject to 2% monthly interest."))
    
    # 4. Add line items using the line item builder
    print("\n4. Adding Line Items...")
    line_item_builder = client.create_line_item_builder()
    
    # Item 1: Laptop (Standard VAT)
    item1 = (line_item_builder
        .with_description("Dell Latitude 5520 Laptop")
        .with_hsn_code("8471")  # HSN for computers
        .with_product_code("LAP-DELL-5520")
        .with_quantity(2, UnitOfMeasure.PIECE)
        .with_unit_price(Decimal("150000.00"))
        .with_discount_percent(Decimal("10"))  # 10% discount
        .with_tax(Decimal("7.5"))  # 7.5% VAT
        .build())
    
    # Reset builder for next item
    line_item_builder.reset()
    
    # Item 2: Software License (Service)
    item2 = (line_item_builder
        .with_description("Microsoft Office 365 Business License (1 Year)")
        .with_hsn_code("9984")  # SAC for software services
        .with_product_code("SW-MS365-BUS")
        .with_quantity(10, UnitOfMeasure.UNIT)
        .with_unit_price(Decimal("12000.00"))
        .with_tax(Decimal("7.5"))
        .build())
    
    # Reset builder for next item
    line_item_builder.reset()
    
    # Item 3: Medical Equipment (VAT Exempt)
    item3 = (line_item_builder
        .with_description("Digital Blood Pressure Monitor")
        .with_hsn_code("9018")  # HSN for medical instruments (VAT exempt)
        .with_product_code("MED-BPM-001")
        .with_quantity(5, UnitOfMeasure.PIECE)
        .with_unit_price(Decimal("8000.00"))
        .with_tax_exemption("Medical equipment - VAT exempt under FIRS guidelines")
        .build())
    
    # Add items to invoice builder
    invoice_builder.add_line_item(item1)
    invoice_builder.add_line_item(item2)
    invoice_builder.add_line_item(item3)
    
    print(f"   ✓ Added 3 line items")
    
    # Build the final invoice
    invoice = invoice_builder.build()
    print(f"   ✓ Invoice Number: {invoice.invoice_number}")
    print(f"   ✓ Invoice Type: {invoice.invoice_type}")
    
    # 5. Display invoice summary
    print("\n5. Invoice Summary:")
    print("-" * 40)
    for idx, item in enumerate(invoice.line_items, 1):
        print(f"   Item {idx}: {item.description}")
        print(f"      Quantity: {item.quantity} {item.unit_of_measure}")
        print(f"      Unit Price: ₦{item.unit_price:,.2f}")
        print(f"      Line Total: ₦{item.line_total:,.2f}")
        if item.tax_exempt:
            print(f"      Tax: EXEMPT - {item.tax_exempt_reason}")
        else:
            print(f"      Tax ({item.tax_rate}%): ₦{item.tax_amount:,.2f}")
    
    print("-" * 40)
    print(f"   Subtotal: ₦{invoice.subtotal:,.2f}")
    print(f"   Total Discount: ₦{invoice.total_discount:,.2f}")
    print(f"   Total Tax: ₦{invoice.total_tax:,.2f}")
    print(f"   TOTAL AMOUNT: ₦{invoice.total_amount:,.2f}")
    
    # 6. Validate invoice
    print("\n6. Validating Invoice...")
    validation_result = client.validate_invoice(invoice)
    
    if validation_result.valid:
        print("   ✓ Invoice is valid")
    else:
        print("   ✗ Invoice validation failed:")
        for error in validation_result.errors:
            print(f"      - {error.field}: {error.message}")
    
    # 7. Generate IRN
    print("\n7. Generating Invoice Reference Number (IRN)...")
    irn = client.generate_irn(invoice)
    invoice.irn = irn
    print(f"   ✓ IRN: {irn}")
    
    # 8. Generate QR Code
    print("\n8. Generating QR Code...")
    qr_data = await client.generate_qr_code(invoice)
    print(f"   ✓ QR Code data generated")
    print(f"   ✓ QR Data (JSON): {qr_data[:100]}...")
    
    # 9. Save invoice to file
    print("\n9. Saving Invoice to File...")
    file_path = client.save_invoice_to_file(invoice)
    print(f"   ✓ Invoice saved to: {file_path}")
    
    # 10. Submit invoice (simulated)
    print("\n10. Submitting Invoice to FIRS...")
    submission_result = await client.submit_invoice(invoice)
    
    if submission_result.success:
        print(f"   ✓ Invoice submitted successfully")
        print(f"   ✓ Submission Date: {submission_result.submission_date}")
        print(f"   ✓ Status: {submission_result.status}")
        print(f"   ✓ Reference Number: {submission_result.reference_number}")
    else:
        print("   ✗ Invoice submission failed")
    
    # 11. Display Pydantic model features
    print("\n11. Pydantic Model Features:")
    print("-" * 40)
    
    # Show model export capabilities
    print("   Model Export Formats:")
    print(f"      - Dict: {type(invoice.model_dump())}")
    print(f"      - JSON: {invoice.model_dump_json()[:50]}...")
    
    # Show computed fields
    print("\n   Computed Fields (automatic calculation):")
    print(f"      - Subtotal: ₦{invoice.subtotal:,.2f}")
    print(f"      - Total Tax: ₦{invoice.total_tax:,.2f}")
    print(f"      - Total Amount: ₦{invoice.total_amount:,.2f}")
    
    # Show validation
    print("\n   Validation Features:")
    print("      - Automatic field validation")
    print("      - Nigerian phone number validation")
    print("      - TIN format validation")
    print("      - HSN code validation")
    print("      - Email validation")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())