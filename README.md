# FIRS E-Invoice Python SDK

A Python SDK for integrating with the Federal Inland Revenue Service (FIRS) E-Invoicing platform in Nigeria. Built with Pydantic v2 for robust data validation and type safety.

## Features

- 🔐 **Secure API Integration** - Complete FIRS API client with authentication
- ✅ **Pydantic Validation** - Full data validation using Pydantic v2 models
- 🏗️ **Builder Pattern** - Fluent interface for invoice construction
- 🔢 **HSN Code Management** - Harmonized System of Nomenclature support
- 💰 **Tax Calculation** - Automatic VAT and tax calculations
- 🔏 **Digital Signing** - PKI-based invoice signing
- 📱 **QR Code Generation** - FIRS-compliant QR codes
- 💾 **Caching** - Smart resource caching for performance
- 🌍 **Nigerian Standards** - Built for Nigerian tax compliance

## Installation

### Quick Setup with Poetry (Recommended)

#### Automated Setup

Clone the repository and run the setup script:

**Unix/Linux/Mac:**
```bash
git clone https://github.com/firs-einvoice/firs-einvoice-py.git
cd firs-einvoice-py
chmod +x setup.sh
./setup.sh
```

**Windows:**
```batch
git clone https://github.com/firs-einvoice/firs-einvoice-py.git
cd firs-einvoice-py
setup.bat
```

#### Manual Setup with Poetry

1. **Create and activate virtual environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Unix/Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate.bat
```

2. **Install Poetry and dependencies:**
```bash
# Install Poetry
pip install --upgrade pip
pip install poetry

# Configure Poetry to use the virtual environment
poetry config virtualenvs.in-project true
poetry config virtualenvs.create false

# Install dependencies
poetry install
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your FIRS API credentials
```

### Using Make (Unix/Linux/Mac)

If you have `make` installed:

```bash
make setup          # Complete setup
make dev            # Install with dev dependencies
make run-example    # Run the example
make test           # Run tests
make clean          # Clean build artifacts
```

### Installing from PyPI

Once published to PyPI:
```bash
pip install firs-einvoice
```

Or with Poetry:
```bash
poetry add firs-einvoice
```

## Quick Start

```python
from firs_einvoice import FIRSClient
from firs_einvoice.models import Party, Address

# Initialize client with credentials
client = FIRSClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    business_id="your_business_id"
)

# Create an invoice using the builder pattern
invoice_builder = client.create_invoice_builder()

invoice = (invoice_builder
    .with_invoice_number("INV-2024-001")
    .with_invoice_type("STANDARD")
    .with_supplier(supplier_party)
    .with_customer(customer_party)
    .add_line_item(
        description="Product A",
        hsn_code="1234",
        quantity=10,
        unit_price=100.00
    )
    .build())

# Validate locally
validation_result = client.validate_invoice(invoice)

# Submit to FIRS
if validation_result.success:
    submission_result = await client.submit_invoice(invoice)
    print(f"IRN: {submission_result.irn}")
    
    # Generate QR code
    qr_path = await client.generate_qr_code_to_file(invoice, "invoice_qr.png")
    print(f"QR Code saved to: {qr_path}")
```

## Pydantic Models

All data structures are defined using Pydantic v2 for automatic validation:

```python
from firs_einvoice.models import Invoice, Party, LineItem
from decimal import Decimal

# Pydantic models with automatic validation
party = Party(
    business_id="BUS123",
    tin="12345678",  # Automatically validated
    name="ABC Company Ltd",
    email="info@abc.com",  # Email validation
    phone="08012345678",  # Nigerian phone validation
    address=Address(
        street="123 Main St",
        city="Lagos",
        state_code="LA",
        country_code="NG"
    )
)

# Validation errors are raised automatically
try:
    invalid_party = Party(
        business_id="123",
        tin="invalid",  # Will raise validation error
        # ... other fields
    )
except ValidationError as e:
    print(e.errors())
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
FIRS_API_KEY=your_api_key
FIRS_API_SECRET=your_api_secret
FIRS_BUSINESS_ID=your_business_id
FIRS_TIN=your_tin
FIRS_BUSINESS_NAME=Your Business Name
FIRS_BASE_URL=https://api.firs.gov.ng/api/v1
```

### Programmatic Configuration

```python
from firs_einvoice.config import FIRSConfig

config = FIRSConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    business_id="your_business_id",
    timeout=30,
    max_retries=3
)

client = FIRSClient(config=config)
```

## Advanced Features

### HSN Code Management

```python
from firs_einvoice.managers import HSNManager

hsn_manager = HSNManager()

# Add custom HSN codes
hsn_manager.add_hsn_code(
    code="9018",
    description="Medical instruments",
    tax_rate=Decimal("0"),  # VAT exempt
    category="MEDICAL"
)

# Validate HSN codes
is_valid = hsn_manager.validate_hsn("9018")
```

### Tax Calculation

```python
from firs_einvoice.managers import TaxManager

tax_manager = TaxManager()

# Calculate taxes for line items
tax_calculation = tax_manager.calculate_tax(
    base_amount=Decimal("1000"),
    tax_rate=Decimal("7.5"),
    discount_percent=Decimal("10")
)

print(f"Tax Amount: {tax_calculation.tax_amount}")
print(f"Total: {tax_calculation.total_amount}")
```

### Digital Signing

```python
from firs_einvoice.crypto import FIRSSigner

signer = FIRSSigner(
    private_key_path="path/to/private_key.pem",
    certificate_path="path/to/certificate.pem"
)

# Sign invoice data
signed_data = signer.sign_invoice(invoice)
```

### Batch Operations

```python
# Validate multiple invoices
invoices = [invoice1, invoice2, invoice3]
results = await client.batch_validate_invoices(invoices)

# Bulk submission
submission_results = await client.batch_submit_invoices(invoices)
```

### Resource Caching

```python
# Preload all resources for offline use
await client.preload_resources()

# Get cached resources
vat_exemptions = await client.get_vat_exemptions()
states = await client.get_states()
lgas = await client.get_lgas("LA")  # Get LGAs for Lagos state
```

## API Endpoints

The SDK supports all FIRS E-Invoice API endpoints:

- **Invoice Operations**
  - `POST /api/v1/invoice/validate` - Validate invoice
  - `POST /api/v1/invoice/submit` - Submit invoice
  - `GET /api/v1/invoice/status/{irn}` - Get status
  - `POST /api/v1/invoice/cancel` - Cancel invoice

- **Resource Endpoints**
  - `GET /api/v1/invoice/resources/invoice-types`
  - `GET /api/v1/invoice/resources/tax-categories`
  - `GET /api/v1/invoice/resources/vat-exemptions`
  - `GET /api/v1/invoice/resources/states`
  - `GET /api/v1/invoice/resources/lgas`

## Error Handling

```python
from firs_einvoice.exceptions import (
    FIRSAPIError,
    ValidationError,
    AuthenticationError
)

try:
    result = await client.submit_invoice(invoice)
except ValidationError as e:
    print(f"Validation failed: {e.errors()}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except FIRSAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=firs_einvoice

# Run specific test file
pytest tests/test_models.py
```

## Examples

See the `examples/` directory for complete working examples:

- `simple_invoice.py` - Basic invoice creation
- `qr_code_demo.py` - QR code generation
- `firs_signing_demo.py` - Digital signing
- `api_integration.py` - Full API workflow

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/firs-einvoice/firs-einvoice-py.git
cd firs-einvoice-py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### Code Quality

```bash
# Format code with black
black firs_einvoice

# Sort imports
isort firs_einvoice

# Type checking
mypy firs_einvoice

# Linting
flake8 firs_einvoice
```

## Documentation

Full documentation is available at [https://firs-einvoice-py.readthedocs.io](https://firs-einvoice-py.readthedocs.io)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: [https://github.com/firs-einvoice/firs-einvoice-py/issues](https://github.com/firs-einvoice/firs-einvoice-py/issues)
- Documentation: [https://firs-einvoice-py.readthedocs.io](https://firs-einvoice-py.readthedocs.io)

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial release with full Pydantic v2 support
- Complete FIRS API integration
- Digital signing and QR code generation

## Publishing

By default we publish to GitHub’s Python package registry (GitHub Packages) on version tags `v*`.

Workflow: `.github/workflows/publish-github-packages.yml`

Trigger a publish by tagging and pushing:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Install from GitHub Packages (replace OWNER with your org/user):

```bash
pip install --index-url https://pypi.pkg.github.com/OWNER/simple/ --extra-index-url https://pypi.org/simple/ zutax-sdk-py
```

Alternatively, PyPI publishing is available via a separate workflow and tag namespace (`pypi-v*`): `.github/workflows/publish-pypi.yml`.
- Comprehensive validation and error handling