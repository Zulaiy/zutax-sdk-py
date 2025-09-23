# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zutax (by Zulaiy) - Python SDK for Nigerian FIRS e-Invoicing platform. The SDK provides Pydantic v2 validation, fluent builders, IRN/QR utilities, and API helpers for e-invoice submission and management.

## Development Commands

### Environment Setup
```bash
# Complete setup (recommended)
./setup.sh   # Creates venv, installs Poetry, dependencies, and .env

# Alternative setup methods
make setup   # Using Makefile
make dev     # Install all dependencies including dev
make install # Production dependencies only

# Manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
cp .env.example .env  # Edit with your credentials
```

### Testing
```bash
# Run all tests
pytest tests/ -v
make test

# Run specific test files
pytest tests/test_models.py -v
pytest tests/test_builders.py -v

# Run with coverage
pytest tests/ --cov=zutax --cov-report=html
```

### Code Quality
```bash
# Format code (targets zutax/ not firs_einvoice/ - Makefile needs fixing)
poetry run black zutax/
poetry run isort zutax/

# Type checking
poetry run mypy zutax/

# Linting
poetry run flake8 zutax/
```

### Running Examples
```bash
# Simple invoice example
poetry run python examples/simple_invoice.py
make run-example

# Comprehensive example
poetry run python examples/comprehensive_example.py
```

### Build and Distribution
```bash
make build     # Creates distribution packages in dist/
make clean     # Clean build artifacts and cache
make clean-all # Clean everything including venv
```

## Architecture

### Core Components

1. **ZutaxClient** (`zutax/client.py`) - Main SDK entry point
   - Configuration management via ZutaxConfig
   - Invoice/LineItem builders
   - Local validation using Pydantic
   - Async API operations (submit, status)
   - IRN generation and QR code creation

2. **Models** (`zutax/models/`) - Pydantic v2 data models
   - `invoice.py` - Invoice model with computed fields
   - `party.py` - Supplier/customer party information
   - `line_item.py` - Invoice line items with tax calculations
   - `enums.py` - All enumeration types (StateCode, PaymentMethod, etc.)
   - `base.py` - Base model classes

3. **Builders** (`zutax/builders/`) - Fluent interface for object creation
   - `invoice_builder.py` - Chain methods to build invoices
   - `line_item_builder.py` - Build line items with tax calculations

4. **Configuration** (`zutax/config/`)
   - `settings.py` - Pydantic Settings with env variable support
   - `constants.py` - Default values and constants
   - Uses `.env` file with FIRS_ prefix

5. **API Layer** (`zutax/api/`)
   - `client.py` - HTTP client with auth and retry logic
   - `invoice.py` - Invoice-specific API operations
   - `resources.py` - State/LGA resource APIs

6. **Crypto** (`zutax/crypto/`)
   - `irn.py` - IRN (Invoice Reference Number) generation
   - `firs_qrcode.py` - QR code generation with PIL
   - `firs_signing.py` - Digital signing capabilities

7. **Managers** (`zutax/managers/`)
   - `hsn_manager.py` - HSN code lookup and validation
   - `tax_manager.py` - Tax calculations and rates

### Key Features

- **Pydantic v2 Validation**: All models use Pydantic for strong typing and validation
- **Fluent Builders**: Chain method calls to build complex objects
- **Environment Configuration**: Uses `.env` file with FIRS_ prefix
- **Async API Support**: Submit invoices and check status asynchronously
- **IRN Generation**: Format: `{SanitizedInvoice}-{ServiceID8}-{YYYYMMDD}-{OriginalInvoice}`
- **QR Code Generation**: Base64 or file output with customization options

### Test Structure

- **Fixtures** (`tests/conftest.py`) - Common test data and client setup
- **Model Tests** - Pydantic validation and computed fields
- **Builder Tests** - Fluent interface functionality
- **API Tests** - Mock HTTP responses and error handling
- **Integration Tests** - End-to-end example execution

## Configuration

The SDK uses Pydantic Settings with environment variables:

### Required Environment Variables
```bash
FIRS_API_KEY=your_api_key
FIRS_API_SECRET=your_api_secret
FIRS_BUSINESS_ID=your_business_id
FIRS_BUSINESS_NAME=Your Business Name
FIRS_TIN=12345678901
```

### Optional Configuration
```bash
FIRS_BASE_URL=https://api.firs.gov.ng/api/v1
FIRS_SERVICE_ID=YOURSRV1  # 8 chars for IRN generation
FIRS_OUTPUT_DIR=./output
FIRS_TIMEOUT=30
FIRS_MAX_RETRIES=3
```

## Common Patterns

### Creating an Invoice
```python
from zutax import ZutaxClient, ZutaxConfig

# Initialize client
config = ZutaxConfig(api_key="...", api_secret="...", ...)
client = ZutaxClient(config=config)

# Build invoice using fluent interface
invoice = (
    client.create_invoice_builder()
    .with_invoice_number("INV-001")
    .with_supplier(supplier_party)
    .with_customer(customer_party)
    .add_line_item(line_item)
    .build()
)

# Validate locally
result = client.validate_invoice(invoice)
assert result.valid

# Generate IRN and submit
invoice.irn = client.generate_irn(invoice)
submission = await client.submit_invoice(invoice)
```

### Working with Line Items
```python
line_item = (
    client.create_line_item_builder()
    .with_description("Product A")
    .with_hsn_code("8471")
    .with_quantity(10, UnitOfMeasure.PIECE)
    .with_unit_price(Decimal("1000.00"))
    .with_tax(Decimal("7.5"))
    .build()
)
```

## Important Notes

- Package name: `zutax-firs-einvoice` (pip install)
- Import as: `import zutax`
- Python 3.8+ required
- Uses Poetry for dependency management
- All tests should pass before committing
- Makefile has outdated path references (uses `firs_einvoice/` instead of `zutax/`)
- Examples may fail gracefully in demo mode when API credentials are invalid