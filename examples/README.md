# FIRS E-Invoice Python SDK Examples

This directory contains example scripts demonstrating how to use the FIRS E-Invoice Python SDK.

## Examples

### 1. Simple Invoice (`simple_invoice.py`)

A basic example showing:
- Creating parties (supplier and customer)
- Building an invoice with line items
- Validating the invoice locally
- Generating IRN and QR codes

```bash
python simple_invoice.py
```

### 2. Comprehensive Example (`comprehensive_example.py`)

A complete demonstration of all SDK features:
- Invoice creation and validation
- HSN code management and tax calculations
- Digital signing and QR code generation
- API integration and resource management
- Batch operations and file handling
- Caching and configuration

```bash
python comprehensive_example.py
```

## Features Demonstrated

### Pydantic v2 Integration
- **Automatic Validation**: All models are validated automatically when created
- **Type Coercion**: Strings and numbers are automatically converted to proper types
- **Computed Fields**: Totals and calculations are handled automatically
- **JSON Serialization**: Easy conversion to/from JSON with proper Decimal handling

### Nigerian Compliance
- **TIN Validation**: 8-15 digit Tax Identification Numbers
- **Phone Validation**: Nigerian phone number formats (080x, +234)
- **State Codes**: All 36 states + FCT
- **VAT Handling**: 7.5% VAT with exemptions for medical/food items
- **HSN Codes**: Harmonized System codes for products and services

### Builder Pattern
```python
# Fluent interface for invoice creation
invoice = (builder
    .with_invoice_number("INV-2024-001")
    .with_supplier(supplier)
    .with_customer(customer)
    .add_line_item(item)
    .build())
```

### Tax Scenarios
1. **Standard VAT**: 7.5% on regular items
2. **VAT Exempt**: Medical equipment, food items
3. **Discounts**: Percentage or fixed amount discounts
4. **Multiple Tax Categories**: VAT, Excise, Customs, etc.

## Environment Setup

1. Install the package:
```bash
pip install -e ..
```

2. Set environment variables (optional):
```bash
export FIRS_API_KEY="your_api_key"
export FIRS_API_SECRET="your_api_secret"
export FIRS_BUSINESS_ID="your_business_id"
```

Or create a `.env` file:
```env
FIRS_API_KEY=your_api_key
FIRS_API_SECRET=your_api_secret
FIRS_BUSINESS_ID=your_business_id
FIRS_TIN=12345678
FIRS_BUSINESS_NAME=Your Business Ltd
```

## Common Use Cases

### Creating a Party
```python
from firs_einvoice import Party, Address
from firs_einvoice.models.enums import StateCode

party = Party(
    business_id="BUS-001",
    tin="12345678",
    name="Company Name Ltd",
    email="info@company.ng",
    phone="08012345678",
    address=Address(
        street="123 Main Street",
        city="Lagos",
        state_code=StateCode.LA,
        postal_code="101241"
    )
)
```

### Adding Line Items
```python
from firs_einvoice import LineItemBuilder

item = (LineItemBuilder()
    .with_description("Product Name")
    .with_hsn_code("1234")
    .with_quantity(10)
    .with_unit_price(1000.00)
    .with_discount_percent(10)
    .with_tax(7.5)
    .build())
```

### Handling VAT Exemptions
```python
# Medical equipment - automatically VAT exempt
medical_item = (LineItemBuilder()
    .with_description("Medical Device")
    .with_hsn_code("9018")  # Medical HSN code
    .with_quantity(1)
    .with_unit_price(5000.00)
    .build())  # Tax automatically set to 0 for medical items
```

## Error Handling

The SDK uses Pydantic's validation to catch errors early:

```python
from pydantic import ValidationError

try:
    invoice = builder.build()
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Error: {error['msg']}")
```

## Next Steps

- Review the main package documentation
- Check the API integration guide
- Explore advanced features like batch processing
- Implement digital signing with PKI certificates