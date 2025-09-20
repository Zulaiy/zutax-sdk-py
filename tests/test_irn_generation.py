#!/usr/bin/env python3
"""Test IRN generation with FIRS_SERVICE_ID from .env."""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import after loading .env
from zutax.crypto.irn import IRNGenerator
from zutax import ZutaxClient as FIRSClient, ZutaxConfig as FIRSConfig

def test_irn_generation():
    """Test IRN generation with proper FIRS_SERVICE_ID."""
    
    print("Testing IRN Generation with FIRS Specification")
    print("=" * 50)
    
    # Verify FIRS_SERVICE_ID is loaded from .env
    service_id = os.environ.get('FIRS_SERVICE_ID')
    print(f"\n🔑 FIRS_SERVICE_ID from .env: {service_id}")
    
    if not service_id:
        print("⚠️  WARNING: FIRS_SERVICE_ID not found in .env")
        print("   IRN will use fallback generation")
    
    # Create test invoice object
    class TestInvoice:
        def __init__(self, invoice_number, issue_date=None):
            self.invoice_number = invoice_number
            self.issue_date = issue_date or datetime.now()
    
    # Test 1: Generate IRN with IRNGenerator
    print("\n1️⃣  Testing IRNGenerator.generate_irn():")
    test_invoice = TestInvoice("INV-2024-001")
    irn = IRNGenerator.generate_irn(test_invoice)
    print(f"   Generated IRN: {irn}")
    
    # Parse and validate IRN
    components = IRNGenerator.extract_components(irn)
    print(f"   Invoice Number: {components['invoice_number']}")
    print(f"   Service ID: {components['service_id']}")
    print(f"   Date Stamp: {components['date_stamp']}")
    
    # Verify service ID matches .env
    if service_id:
        assert (
            components['service_id'] == service_id[:8].upper()
        ), (
            "Service ID mismatch! Expected {} got {}".format(
                service_id, components['service_id']
            )
        )
        print(f"   ✅ Service ID matches .env: {components['service_id']}")
    
    # Test 2: Generate IRN with FIRSClient
    print("\n2️⃣  Testing FIRSClient.generate_irn():")
    config = FIRSConfig(
        api_key="test_key",
        api_secret="test_secret",
        business_id="TEST-BUS",
        business_name="Test Business",
        tin="12345678901"
    )
    client = FIRSClient(config=config)
    
    # Create mock invoice with required fields
    class MockInvoice:
        def __init__(self):
            self.invoice_number = "INV-2024-002"
            self.issue_date = datetime.now()
    
    mock_invoice = MockInvoice()
    client_irn = client.generate_irn(mock_invoice)
    print(f"   Generated IRN: {client_irn}")
    
    # Parse client IRN
    client_components = client_irn.split('-')
    print(f"   Invoice Number: {'-'.join(client_components[:-2])}")
    print(f"   Service ID: {client_components[-2]}")
    print(f"   Date Stamp: {client_components[-1]}")
    
    if service_id:
        assert (
            client_components[-2] == service_id[:8].upper()
        ), "Client Service ID mismatch!"
        print(f"   ✅ Service ID matches .env: {client_components[-2]}")
    
    # Test 3: Generate IRN with specific date
    print("\n3️⃣  Testing IRN with specific date:")
    specific_date = datetime(2024, 6, 11)  # June 11, 2024
    test_invoice_dated = TestInvoice("INV001", specific_date)
    irn_dated = IRNGenerator.generate_irn(test_invoice_dated)
    print(f"   Generated IRN: {irn_dated}")
    
    # Should match FIRS example format
    print("   Expected format: INV001-[SERVICE_ID]-20240611")
    
    if service_id:
        expected_irn = f"INV001-{service_id[:8].upper()}-20240611"
        assert (
            irn_dated == expected_irn
        ), "IRN format mismatch! Expected {} got {}".format(expected_irn, irn_dated)
        print("   ✅ Matches FIRS specification format!")
    
    # QR generation steps removed in minimal test suite cleanup
    
    # Save test results
    results = {
        "timestamp": datetime.now().isoformat(),
        "service_id_from_env": service_id,
        "test_results": {
            "irn_generator": {
                "irn": irn,
                "components": {
                    "invoice_number": components['invoice_number'],
                    "service_id": components['service_id'],
                    "date_stamp": components['date_stamp']
                }
            },
            "firs_client": {
                "irn": client_irn,
                "service_id": client_components[-2]
            },
            "dated_example": {
                "irn": irn_dated,
                "matches_spec": irn_dated == f"INV001-{service_id[:8].upper() if service_id else 'GENERATED'}-20240611"
            }
        },
    "qr_file": None
    }
    
    import tempfile
    from pathlib import Path
    tmp_dir = Path(tempfile.gettempdir())
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    results_file = tmp_dir / f"irn_test_results_{ts}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file}")
    print("\n✅ IRN Generation Test Complete!")
    
    if service_id:
        print(f"\n🎯 All IRNs using FIRS_SERVICE_ID: {service_id}")
    else:
        print("\n⚠️  Add FIRS_SERVICE_ID to .env for production use!")


if __name__ == "__main__":
    test_irn_generation()
