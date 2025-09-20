# ZUTAX – FIRS E‑Invoice Python SDK (by Zulaiy)

Python SDK for integrating with Nigeria’s Federal Inland Revenue Service (FIRS) e‑Invoicing platform. Uses Pydantic v2 for strong typing and validation, and provides builders, IRN/QR utilities, and simple API helpers.

## Features

- ✅ Pydantic v2 validation for all models
- 🏗️ Fluent builders for invoices and line items
- 🔢 HSN support and tax helpers
- � IRN generation utility following FIRS format
- 📱 QR code generation (base64 or file)
- 🌐 Basic API helpers (submit/status) with retries
- 💾 Optional caching hooks (extensible)

## Installation

You can use Poetry (recommended) or plain pip. The package installs as `zutax-firs-einvoice` and is imported as `zutax`.

### Quick start with Poetry

1) Clone and set up

```bash
git clone https://github.com/Zulaiy/zutax-sdk-py.git
cd zutax-sdk-py
./setup.sh   # on Linux/macOS (or run the steps below manually)
```

2) Manual steps (if not using setup.sh)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.create false
poetry install
cp .env.example .env  # then edit with your values
```

### Using Make (Linux/macOS)

```bash
make setup       # bootstrap env and install deps
make dev         # install with dev dependencies
make test        # run tests
```

### Install via pip (when published)

```bash
pip install zutax-firs-einvoice
```

## Quick start

Minimal end‑to‑end flow using builders, validation, IRN, and QR. The async parts run inside `asyncio.run(...)`.

```python
import asyncio
from decimal import Decimal
from datetime import datetime

from zutax import (
    ZutaxClient, ZutaxConfig,
    Party, Address, PaymentDetails,
    InvoiceType, PaymentMethod,
)
from zutax.models.enums import StateCode, UnitOfMeasure


async def main():
    # Configure client (env vars also supported)
    config = ZutaxConfig(
        api_key="your_api_key",
        api_secret="your_api_secret",
        business_id="YOUR-BUS-ID",
        business_name="Your Business Ltd",
        tin="12345678901",
        service_id="YOURSRV1",  # 8 chars preferred
    )
    client = ZutaxClient(config=config)

    # Parties
    supplier = Party(
        business_id="SUP-001",
        tin="12345678901",
        name="Supplier Ltd",
        email="info@supplier.ng",
        phone="08012345678",
        address=Address(street="1 Main St", city="Lagos", state_code=StateCode.LA)
    )
    customer = Party(
        business_id="CUS-001",
        tin="10987654321",
        name="Customer Ltd",
        email="purchasing@customer.ng",
        phone="08087654321",
        address=Address(street="2 Broad St", city="Abuja", state_code=StateCode.FC)
    )

    payment = PaymentDetails(method=PaymentMethod.BANK_TRANSFER)

    # Build invoice
    invoice = (
        client.create_invoice_builder()
        .with_invoice_number("INV-2025-000001")
        .with_invoice_type(InvoiceType.STANDARD)
        .with_invoice_date(datetime.now())
        .with_supplier(supplier)
        .with_customer(customer)
        .with_payment_details(payment)
        .add_line_item(
            client.create_line_item_builder()
            .with_description("Product A")
            .with_hsn_code("8471")
            .with_quantity(2, UnitOfMeasure.PIECE)
            .with_unit_price(Decimal("150000.00"))
            .with_tax(Decimal("7.5"))
            .build()
        )
        .build()
    )

    # Validate
    result = client.validate_invoice(invoice)
    assert result.valid, f"Validation failed: {result.errors}"

    # IRN & QR
    invoice.irn = client.generate_irn(invoice)
    qr_path = await client.generate_qr_code_to_file(invoice)
    print("IRN:", invoice.irn)
    print("QR saved:", qr_path)

    # Optional: submit (requires working credentials/network)
    # submission = await client.submit_invoice(invoice)
    # print("Submitted:", submission.success, submission.status)


if __name__ == "__main__":
    asyncio.run(main())
```

## Models and validation

All core data is modeled with Pydantic v2. Invalid data will raise validation errors upon model construction or explicit validation.

## Configuration

Environment variables (via `.env`) are supported and/or you can pass a `ZutaxConfig`.

Environment keys commonly used:

```env
FIRS_API_KEY=your_api_key
FIRS_API_SECRET=your_api_secret
BUSINESS_ID=your_business_id
BUSINESS_NAME=Your Business Name
TIN=12345678901
FIRS_SERVICE_ID=YOURSRV1
FIRS_BASE_URL=https://api.firs.gov.ng/api/v1
```

Programmatic configuration:

```python
from zutax import ZutaxClient, ZutaxConfig

client = ZutaxClient(config=ZutaxConfig(
    api_key="your_api_key",
    api_secret="your_api_secret",
    business_id="YOUR-BUS-ID",
))
```

## Common tasks

### HSN and tax helpers

```python
from zutax import HSNManager, TaxManager
from decimal import Decimal

hsn = HSNManager()
tax = TaxManager()

info = hsn.get_hsn_code("9018")  # medical instruments (often VAT exempt)
calc = tax.calculate_line_tax(amount=100000.0, custom_rate=7.5)
```

### Digital signing (when configured)

```python
from zutax import ZutaxSigner as FIRSSigner

signer = FIRSSigner()
if hasattr(signer, "sign_invoice"):
    signature = signer.sign_invoice(invoice)
```

### Batch operations

```python
results = await client.batch_validate_invoices([inv1, inv2])
submissions = await client.batch_submit_invoices([inv1, inv2])
```

### Resources and caching (placeholders)

```python
await client.preload_resources()
states = await client.get_states()
lgas = await client.get_lgas("LA")
```

## API helpers (submit, status)

Minimal wrappers are included for common calls. In demo/local use, these often require stubbing/mocking unless you have valid credentials and access.

- Submit invoice: `await client.submit_invoice(invoice)`
- Get status: `await client.get_invoice_status(irn)`
- Cancel (stub): `await client.cancel_invoice(irn, reason)`

## Error handling

API calls return structured results; validation returns a `FIRSValidationResponse` with `valid`, `errors`, `warnings`.

## Testing

Run with pytest:

```bash
pytest -q
```

Notes:
- Some QR tests require `FIRS_PUBLIC_KEY` and `FIRS_CERTIFICATE` env vars and `pycryptodome`.
- Example tests run the scripts under `examples/` and expect network/API to be unavailable in demo mode, so they handle failures gracefully.

## Examples

See `examples/` for runnable demos:

- `simple_invoice.py` – basic invoice, validation, IRN, QR
- `comprehensive_example.py` – multiple items, HSN/tax showcase, signing demo

## Development

```bash
git clone https://github.com/Zulaiy/zutax-sdk-py.git
cd zutax-sdk-py
python -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt  # if present, or use Poetry group dev
```

Quality tools (if you use them):

```bash
black zutax
isort zutax
mypy zutax
flake8 zutax
```

## Documentation

Inline docstrings and examples are the primary reference for now. Additional docs may be added.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open issues and PRs on the GitHub repo under the Zulaiy organization.

## Support

For issues and questions:
- GitHub Issues: https://github.com/Zulaiy/zutax-sdk-py/issues

## Changelog

See Git history and releases in the repository.

— Built and maintained by Zulaiy.