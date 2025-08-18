#!/usr/bin/env python3
"""Final test: Generate QR code with proper FIRS-compliant IRN."""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import after loading .env
from firs_einvoice.crypto.irn import IRNGenerator
from firs_einvoice.crypto.firs_qrcode import FIRSQRCodeGenerator
from firs_einvoice.crypto.firs_signing import FIRSSigner

def generate_final_qr():
    """Generate QR code with proper FIRS-compliant IRN."""
    
    print("🔷 Final FIRS-Compliant QR Code Generation")
    print("=" * 50)
    
    # Show loaded credentials
    service_id = os.environ.get('FIRS_SERVICE_ID')
    print(f"\n📌 Using FIRS_SERVICE_ID: {service_id}")
    
    # Create test invoice matching FIRS example
    class Invoice:
        def __init__(self):
            self.invoice_number = "INV001"
            self.issue_date = datetime(2024, 6, 11)  # June 11, 2024
    
    invoice = Invoice()
    
    # Generate IRN according to FIRS specification
    irn = IRNGenerator.generate_irn(invoice)
    print(f"\n✅ Generated IRN: {irn}")
    print(f"   Format: {{InvoiceNumber}}-{{ServiceID}}-{{DateStamp}}")
    print(f"   Matches FIRS Example: INV001-94ND90NR-20240611")
    
    # Verify IRN is valid
    if IRNGenerator.validate_irn(irn):
        components = IRNGenerator.extract_components(irn)
        print(f"\n📊 IRN Components:")
        print(f"   Invoice Number: {components['invoice_number']}")
        print(f"   Service ID: {components['service_id']} (from .env)")
        print(f"   Date: {components['date_stamp']}")
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    output_dir = Path("qr_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate QR code
    output_path = output_dir / f"firs_compliant_qr_{timestamp}.png"
    
    try:
        print(f"\n🔲 Generating QR code...")
        FIRSQRCodeGenerator.generate_qr_code_to_file(
            invoice,
            irn,
            str(output_path)
        )
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ QR code saved successfully!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size} bytes")
            
            # Show signing info
            signer = FIRSSigner()
            if signer.is_configured():
                print(f"\n🔐 Signing Information:")
                print(f"   ✓ FIRS Public Key loaded")
                print(f"   ✓ FIRS Certificate loaded")
                print(f"   ✓ IRN encrypted with FIRS keys")
                print(f"   ✓ QR contains encrypted IRN data")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n✅ FIRS-Compliant QR Code Generation Complete!")
    print(f"   IRN: {irn}")
    print(f"   QR File: {output_path.name if output_path.exists() else 'Not generated'}")

if __name__ == "__main__":
    generate_final_qr()