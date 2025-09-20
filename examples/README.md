# FIRS E-Invoice Python SDK Examples

This directory contains updated example scripts demonstrating how to use the FIRS E-Invoice Python SDK. All examples have been updated to match the current codebase implementation.

## Setup

Before running the examples, install the required dependencies:

```bash
pip install python-dotenv pydantic[email] pydantic-settings pycryptodome qrcode[pil] requests httpx
```

## Examples

### 1. Simple Invoice (`simple_invoice.py`)

A basic example showing:
- Creating parties (supplier and customer) 
- Building an invoice with line items using the fluent builder pattern
- Validating the invoice locally
- Generating IRN and QR codes
- Error handling for demo mode

**Key Features Demonstrated:**
- Current builder pattern with `with_` methods
- Proper Pydantic model usage
- Tax calculations and exemptions
- Payment details integration

```bash
cd /path/to/zutax-sdk-py
PYTHONPATH=/path/to/zutax-sdk-py python examples/simple_invoice.py
```

### 2. Comprehensive Example (`comprehensive_example.py`)

A complete demonstration of advanced SDK features:
- Multiple line items with different tax scenarios
- HSN code management
- Tax calculation scenarios
- Digital signing and QR code generation
- Validation and submission workflow

**Note:** Some advanced features (HSN lookup, tax calculations) may show demo errors as they depend on complete database initialization.

```bash
cd /path/to/zutax-sdk-py  
PYTHONPATH=/path/to/zutax-sdk-py python examples/comprehensive_example.py
```

## What Was Updated

### Fixed Issues:
1. **Method Names**: Changed `set_` methods to `with_` methods in builders
2. **Import Statements**: Updated imports to match current module structure
3. **Error Handling**: Added proper exception handling for demo mode
4. **API Methods**: Updated to use correct method signatures:
   - `IRNGenerator.generate_irn()` instead of `generate()`
   - `HSNManager.get_hsn_code()` instead of `get_hsn_info()`  
   - `TaxManager.calculate_line_tax()` instead of `calculate_tax()`

### Current Implementation Patterns:
- **Fluent Builder Pattern**: Use `with_` methods for invoice/line item building
- **Pydantic v2**: All models use Pydantic v2 with proper validation
- **Error Graceful**: Examples handle missing methods/network issues gracefully
- **Nigerian Compliance**: TIN validation, state codes, phone number formats

## Features Demonstrated

### Pydantic v2 Integration
- **Automatic Validation**: All models are validated automatically when created
- **Type Coercion**: Strings and numbers are automatically converted to proper types  
- **Computed Fields**: Totals and calculations are handled automatically
- **JSON Serialization**: Easy conversion to/from JSON with proper Decimal handling

### Nigerian Compliance
- **TIN Validation**: 8-15 digit Tax Identification Numbers
- **Phone Validation**: Nigerian phone number formats (080x, +234)
- **State Codes**: All 36 states + FCT using proper enum values
- **VAT Handling**: 7.5% VAT with exemptions for medical/food items
- **HSN Codes**: Harmonized System codes for products and services

### Builder Pattern
```python
# Fluent interface for invoice creation
invoice_builder = (client.create_invoice_builder()
                  .with_invoice_number("INV-001")
                  .with_invoice_type(InvoiceType.STANDARD)
                  .with_supplier(supplier)
                  .with_customer(customer)
                  .with_payment_details(payment_details))

# Line item building
line_item = (client.create_line_item_builder()
             .with_description("Product Name")
             .with_quantity(2, UnitOfMeasure.PIECE)
             .with_unit_price(Decimal("100.00"))
             .with_tax(Decimal("7.5"))
             .build())
```

### Error Handling
Examples now properly handle:
- Network connection issues (API calls)
- Missing method implementations (demo mode)
- Validation errors
- File I/O issues

## Production vs Demo Mode

**Demo Mode** (no credentials):
- Local validation works
- IRN generation works  
- File saving works
- API calls fail gracefully with informative messages

**Production Mode** (with proper credentials):
- All features work including API submission
- Real FIRS integration
- Digital signatures
- Complete QR code generation

## Environment Variables

Create a `.env` file for production:

```env
FIRS_API_KEY=your_api_key
FIRS_API_SECRET=your_api_secret
FIRS_SERVICE_ID=your_service_id
BUSINESS_ID=your_business_id
BUSINESS_NAME=Your Business Ltd
TIN=your_tin_number
```
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