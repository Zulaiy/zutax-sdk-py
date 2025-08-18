#!/usr/bin/env python3
"""
Comprehensive example demonstrating advanced FIRS E-Invoice SDK features.

This example demonstrates:
- Invoice creation with multiple line items and tax scenarios
- HSN code management and VAT exemptions
- Digital signing and QR code generation
- Batch processing capabilities
- Resource caching
"""

import os
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
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
    HSNManager,
    TaxManager,
    IRNGenerator,
    FIRSSigner,
    FIRSQRCodeGenerator,
)
from firs_einvoice.models.enums import StateCode, UnitOfMeasure


def create_supplier() -> Party:
    """Create supplier/seller party."""
    return Party(
        business_id="SUP-DEMO-001",
        tin="12345678901",
        name="Tech Solutions Nigeria Ltd",
        trade_name="TechSol",
        email="billing@techsol.ng",
        phone="08012345678",
        address=Address(
            street="123 Victoria Island",
            street2="Suite 100",
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
    """Create customer/buyer party."""
    return Party(
        business_id="CUS-DEMO-001",
        tin="87654321901",
        name="Global Enterprises Limited",
        email="procurement@globalent.ng",
        phone="08087654321",
        address=Address(
            street="456 Central Business District",
            city="Abuja",
            state_code=StateCode.FC,
            lga_code="ABUJA-MUNICIPAL",
            postal_code="900271",
        ),
        vat_registered=True,
        vat_number="VAT654321",
    )


async def demonstrate_invoice_creation(client: FIRSClient):
    """Demonstrate comprehensive invoice creation."""
    print("\n" + "="*60)
    print("1. COMPREHENSIVE INVOICE CREATION")
    print("="*60)
    
    # Create invoice builder
    builder = client.create_invoice_builder()
    
    # Set invoice details using fluent interface
    builder = (builder
        .with_invoice_number("COMP-2024-001")
        .with_invoice_type(InvoiceType.STANDARD)
        .with_invoice_date(datetime.now())
        .with_due_date(datetime.now() + timedelta(days=30))
        .with_supplier(create_supplier())
        .with_customer(create_customer())
        .with_reference_number("PO-2024-999")
        .with_notes("Comprehensive demonstration of SDK features")
        .with_terms_and_conditions("Payment due within 30 days. Late payments subject to 2% monthly interest."))
    
    # Create line item builder
    line_item_builder = client.create_line_item_builder()
    
    # Add diverse line items
    print("\nAdding line items with different tax scenarios...")
    
    # Item 1: Standard taxable item (Computer)
    item1 = (line_item_builder
        .with_description("High-Performance Server - Dell PowerEdge R750")
        .with_hsn_code("8471")  # Computers
        .with_product_code("SRV-DELL-R750")
        .with_quantity(3, UnitOfMeasure.PIECE)
        .with_unit_price(Decimal("850000.00"))
        .with_discount_percent(Decimal("15"))  # 15% bulk discount
        .with_tax(Decimal("7.5"))  # Standard VAT
        .build())
    builder.add_line_item(item1)
    line_item_builder.reset()
    
    # Item 2: Software service (Different HSN)
    item2 = (line_item_builder
        .with_description("Cloud Infrastructure Setup and Configuration Service")
        .with_hsn_code("9984")  # IT services
        .with_product_code("SVC-CLOUD-SETUP")
        .with_quantity(40, UnitOfMeasure.HOUR)  # Changed to HOUR for service
        .with_unit_price(Decimal("6250.00"))  # Price per hour
        .with_tax(Decimal("7.5"))
        .build())
    builder.add_line_item(item2)
    line_item_builder.reset()
    
    # Item 3: VAT-exempt medical equipment
    item3 = (line_item_builder
        .with_description("Portable ECG Machine - Medical Grade")
        .with_hsn_code("9018")  # Medical instruments (VAT exempt)
        .with_product_code("MED-ECG-P100")
        .with_quantity(10, UnitOfMeasure.PIECE)
        .with_unit_price(Decimal("45000.00"))
        .with_tax_exemption("Medical equipment - VAT exempt under FIRS guidelines")
        .build())
    builder.add_line_item(item3)
    line_item_builder.reset()
    
    # Item 4: Basic food item (VAT exempt)
    item4 = (line_item_builder
        .with_description("Rice - Premium Long Grain (50kg bags)")
        .with_hsn_code("1006")  # Rice (VAT exempt)
        .with_product_code("FOOD-RICE-50KG")
        .with_quantity(100, UnitOfMeasure.PACK)  # Changed to PACK
        .with_unit_price(Decimal("28000.00"))
        .with_tax_exemption("Basic food item - VAT exempt")
        .build())
    builder.add_line_item(item4)
    line_item_builder.reset()
    
    # Item 5: Item with additional charges
    item5 = (line_item_builder
        .with_description("Industrial Generator - 500KVA")
        .with_hsn_code("8502")  # Electrical generators
        .with_product_code("GEN-IND-500KVA")
        .with_quantity(1, UnitOfMeasure.PIECE)
        .with_unit_price(Decimal("12500000.00"))
        .with_discount_amount(Decimal("500000.00"))  # Flat discount
        .with_tax(Decimal("7.5"))
        .build())
    builder.add_line_item(item5)
    
    # Build the invoice
    invoice = builder.build()
    
    print(f"✓ Created invoice with {len(invoice.line_items)} diverse line items")
    print(f"✓ Invoice Number: {invoice.invoice_number}")
    
    # Display detailed breakdown
    print("\nDetailed Line Items:")
    print("-" * 80)
    for idx, item in enumerate(invoice.line_items, 1):
        print(f"\nItem {idx}: {item.description}")
        print(f"  HSN Code: {item.hsn_code}")
        print(f"  Quantity: {item.quantity} {item.unit_of_measure}")
        print(f"  Unit Price: ₦{item.unit_price:,.2f}")
        if item.discount_amount > 0:
            print(f"  Discount: ₦{item.discount_amount:,.2f}")
        print(f"  Taxable Amount: ₦{item.taxable_amount:,.2f}")
        if item.tax_exempt:
            print(f"  Tax Status: EXEMPT - {item.tax_exempt_reason}")
        else:
            print(f"  Tax ({item.tax_rate}%): ₦{item.tax_amount:,.2f}")
        print(f"  Line Total: ₦{item.line_total:,.2f}")
    
    print("-" * 80)
    print(f"\nInvoice Summary:")
    print(f"  Subtotal: ₦{invoice.subtotal:,.2f}")
    print(f"  Total Discount: ₦{invoice.total_discount:,.2f}")
    print(f"  Total Charges: ₦{invoice.total_charges:,.2f}")
    print(f"  Total Tax: ₦{invoice.total_tax:,.2f}")
    print(f"  GRAND TOTAL: ₦{invoice.total_amount:,.2f}")
    
    return invoice


async def demonstrate_hsn_management(client: FIRSClient):
    """Demonstrate HSN code management."""
    print("\n" + "="*60)
    print("2. HSN CODE MANAGEMENT")
    print("="*60)
    
    hsn_manager = HSNManager()
    
    # Test various HSN codes
    test_codes = [
        ("8471", "Computers and processing units"),
        ("9018", "Medical instruments"),
        ("1006", "Rice"),
        ("3004", "Medicaments"),
        ("9984", "IT services"),
    ]
    
    print("\nHSN Code Analysis:")
    for code, description in test_codes:
        hsn_code = hsn_manager.get_hsn_code(code)
        is_vat_exempt = hsn_manager.is_exempt(code)
        tax_rate = hsn_manager.get_tax_rate(code)
        print(f"\n{code} - {description}:")
        if hsn_code:
            print(f"  Category: {hsn_code.category}")
        print(f"  VAT Status: {'EXEMPT' if is_vat_exempt else 'TAXABLE'}")
        print(f"  Tax Rate: {tax_rate}%")


async def demonstrate_tax_calculations(client: FIRSClient):
    """Demonstrate tax calculation features."""
    print("\n" + "="*60)
    print("3. TAX CALCULATIONS")
    print("="*60)
    
    tax_manager = TaxManager()
    
    # Test scenarios
    scenarios = [
        ("Standard item", Decimal("100000"), Decimal("7.5"), False),
        ("Discounted item", Decimal("100000"), Decimal("7.5"), False, Decimal("10000")),
        ("VAT-exempt item", Decimal("50000"), Decimal("0"), True),
    ]
    
    print("\nTax Calculation Scenarios:")
    for scenario in scenarios:
        name = scenario[0]
        amount = scenario[1]
        rate = scenario[2]
        exempt = scenario[3]
        discount = scenario[4] if len(scenario) > 4 else Decimal("0")
        
        taxable = amount - discount
        if not exempt:
            tax_calc = tax_manager.calculate_line_tax(float(taxable), custom_rate=float(rate))
            tax_amount = tax_calc.tax_amount
            total = taxable + tax_amount
        else:
            tax_amount = Decimal("0")
            total = taxable
        
        print(f"\n{name}:")
        print(f"  Base Amount: ₦{amount:,.2f}")
        if discount > 0:
            print(f"  Discount: ₦{discount:,.2f}")
        print(f"  Taxable Amount: ₦{taxable:,.2f}")
        if exempt:
            print(f"  Tax Status: EXEMPT")
        else:
            print(f"  Tax Rate: {rate}%")
            print(f"  Tax Amount: ₦{tax_amount:,.2f}")
        print(f"  Total: ₦{total:,.2f}")


async def demonstrate_digital_signing(client: FIRSClient, invoice):
    """Demonstrate digital signing and QR code generation."""
    print("\n" + "="*60)
    print("4. DIGITAL SIGNING & QR CODE GENERATION")
    print("="*60)
    
    # Generate IRN
    print("\nGenerating Invoice Reference Number (IRN)...")
    irn = client.generate_irn(invoice)
    invoice.irn = irn
    print(f"✓ IRN Generated: {irn}")
    
    # Parse IRN components
    irn_parts = IRNGenerator.extract_components(irn)
    print(f"  Invoice Number: {irn_parts['invoice_number']}")
    print(f"  Service ID: {irn_parts['service_id']}")
    print(f"  Date Stamp: {irn_parts['date_stamp']}")
    
    # Digital signing
    print("\nPerforming Digital Signing...")
    try:
        signer = FIRSSigner()
        signing_result = await signer.sign_invoice_for_qr(invoice)
        print(f"✓ Invoice signed successfully")
        print(f"  Signature Length: {len(signing_result.encrypted_data)} characters")
    except Exception as e:
        print(f"✗ Signing skipped (demo mode): {str(e)}")
    
    # Generate QR code
    print("\nGenerating QR Code...")
    qr_generator = FIRSQRCodeGenerator()
    qr_data = await qr_generator.generate_qr_data(invoice)
    print(f"✓ QR Code data generated")
    print(f"  Data preview: {qr_data[:100]}...")
    
    # Save QR code image
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"qr_output/comprehensive_demo_{timestamp}.png"
        await qr_generator.save_qr_code_image(invoice, output_path)
        print(f"✓ QR Code saved to: {output_path}")
    except Exception as e:
        print(f"  Note: {str(e)}")


async def demonstrate_batch_processing(client: FIRSClient):
    """Demonstrate batch invoice processing."""
    print("\n" + "="*60)
    print("5. BATCH PROCESSING")
    print("="*60)
    
    print("\nCreating batch of invoices...")
    invoices = []
    
    for i in range(3):
        builder = client.create_invoice_builder()
        builder = (builder
            .with_invoice_number(f"BATCH-2024-{i+1:03d}")
            .with_invoice_type(InvoiceType.STANDARD)
            .with_invoice_date(datetime.now())
            .with_supplier(create_supplier())
            .with_customer(create_customer()))
        
        # Add a simple line item
        line_item_builder = client.create_line_item_builder()
        item = (line_item_builder
            .with_description(f"Batch Item {i+1}")
            .with_hsn_code("8471")
            .with_quantity(1, UnitOfMeasure.PIECE)
            .with_unit_price(Decimal(str(100000 * (i + 1))))
            .with_tax(Decimal("7.5"))
            .build())
        builder.add_line_item(item)
        
        invoice = builder.build()
        invoices.append(invoice)
        print(f"  ✓ Created invoice {invoice.invoice_number}")
    
    # Batch validation
    print("\nPerforming batch validation...")
    validation_results = await client.batch_validate_invoices(invoices)
    
    for invoice, result in zip(invoices, validation_results):
        status = "✓ VALID" if result.valid else "✗ INVALID"
        print(f"  {invoice.invoice_number}: {status}")
    
    # Generate IRNs for all
    print("\nGenerating IRNs for batch...")
    for invoice in invoices:
        irn = client.generate_irn(invoice)
        invoice.irn = irn
        print(f"  {invoice.invoice_number}: {irn}")


async def main():
    """Main demonstration function."""
    print("="*60)
    print("FIRS E-Invoice Python SDK - Comprehensive Example")
    print("Demonstrates all major SDK features")
    print("="*60)
    
    # Initialize client
    print("\nInitializing FIRS Client...")
    config = FIRSConfig(
        api_key=os.environ.get('FIRS_API_KEY', 'demo_api_key'),
        api_secret=os.environ.get('FIRS_API_SECRET', 'demo_api_secret'),
        business_id=os.environ.get('BUSINESS_ID', 'DEMO-BUS-001'),
        business_name=os.environ.get('BUSINESS_NAME', 'Demo Business Ltd'),
        tin=os.environ.get('TIN', '12345678901'),
        service_id=os.environ.get('FIRS_SERVICE_ID', '94ND90NR')
    )
    
    client = FIRSClient(config=config)
    print("✓ Client initialized successfully")
    
    try:
        # Run demonstrations
        invoice = await demonstrate_invoice_creation(client)
        await demonstrate_hsn_management(client)
        await demonstrate_tax_calculations(client)
        await demonstrate_digital_signing(client, invoice)
        await demonstrate_batch_processing(client)
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("✓ Complex invoice creation with multiple tax scenarios")
        print("✓ HSN code management and VAT exemption detection")
        print("✓ Advanced tax calculations with discounts and charges")
        print("✓ Digital signing and QR code generation")
        print("✓ Batch invoice processing")
        print("✓ IRN generation with FIRS_SERVICE_ID")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("This is expected in demo mode without actual FIRS credentials.")
        print("The example shows how the SDK would work in production.")


if __name__ == "__main__":
    asyncio.run(main())