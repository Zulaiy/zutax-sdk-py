#!/usr/bin/env python3
"""Test script to verify Python QR code image saving with timestamps."""

import os
import json
from pathlib import Path
from datetime import datetime

# Set test keys
os.environ['FIRS_PUBLIC_KEY'] = 'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUE3MUhHUjM2R0oyMWlVM05IMEU2YwpPN2grWnhGcm0vM1dyb05zYXJySEtzSGhtVzdrRy9hU0llZVhXa0M1TVNHbDNSMkxBdUJQdEF2VTIxS0s0YzEwCmVOVWZaSDJoTDZLY1kwN0FSSW1XaU5LUXdxSjJQdGR1bWx3YnJKenBFMjFRc0JISzRMQy9jRzZMQm9waDBzWUoKOWRxRzBNUnpMdmVWckdJM08xcHRKRnNTOUl2Sm8wWFJib015RkdPUjJtRlhJOWUrZE5PYm1OQzVRNFV0Uk93VApRVjlLOHp6TVNkWnRKOEZ3RFdqQ3NpVzJpRmxSSkdWQmlNOTdWdWdTQ0xIWUMzTDJ4Vnc2V2VIYk54TDByVHF2Cm9qUS92ZXVhSnVDRWF1Q3ptTDRJb3Nxc1dJU2tYekpTWFhhRy91eVNtRTRxSW5oZnZJWkE5YzNwMlFDdGZzV2YKM3dJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t'
os.environ['FIRS_CERTIFICATE'] = 'test_cert_short'

from firs_einvoice.crypto.firs_qrcode import FIRSQRCodeGenerator, FIRSQRCodeOptions
from firs_einvoice.crypto.firs_signing import FIRSSigner

def test_python_qr_save():
    """Test that Python saves QR code images correctly with timestamps."""
    
    print("Testing Python QR Code Image Saving with Timestamps")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("qr_output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test data
    test_irn = f"INV-PYTHON-{timestamp}"
    test_invoice = {
        "invoice_number": f"INV-PYTHON-{timestamp}",
        "amount": 1000.00
    }
    
    # Test 1: Generate QR code to file with timestamp
    output_path = output_dir / f"python_qr_{timestamp}.png"
    
    try:
        # Generate QR code and save to file
        FIRSQRCodeGenerator.generate_qr_code_to_file(
            test_invoice, 
            test_irn, 
            str(output_path)
        )
        
        # Check if file was created
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ QR code PNG saved successfully!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size} bytes")
            print(f"   Timestamp: {timestamp}")
        else:
            print(f"❌ Failed to save QR code image")
            
    except Exception as e:
        print(f"❌ Error saving QR code: {e}")
    
    # Test 2: Generate base64 QR code for comparison
    try:
        qr_base64 = FIRSQRCodeGenerator.generate_qr_code(
            test_invoice,
            test_irn
        )
        print(f"\n✅ Base64 QR code generated")
        print(f"   Length: {len(qr_base64)} characters")
        
        # Save base64 to file for reference
        base64_path = output_dir / f"python_qr_base64_{timestamp}.txt"
        with open(base64_path, 'w') as f:
            f.write(qr_base64)
        print(f"   Base64 saved to: {base64_path}")
        
    except Exception as e:
        print(f"❌ Error generating base64 QR: {e}")
    
    # Test 3: Use simple QR method with timestamped output
    simple_output = output_dir / f"python_simple_qr_{timestamp}.png"
    
    try:
        signer = FIRSSigner()
        result = FIRSQRCodeGenerator.generate_simple_qr(
            test_irn,
            signer.get_certificate() or "test_cert",
            signer.get_public_key_pem() or "",
            str(simple_output)
        )
        
        if simple_output.exists():
            print(f"\n✅ Simple QR method also saves PNG!")
            print(f"   File: {simple_output}")
            print(f"   Size: {simple_output.stat().st_size} bytes")
        
    except Exception as e:
        print(f"❌ Error with simple QR: {e}")
    
    # Test 4: Generate with custom options
    custom_output = output_dir / f"python_custom_qr_{timestamp}.png"
    
    try:
        custom_options = FIRSQRCodeOptions(
            box_size=15,  # Larger boxes
            border=6,     # Bigger border
            error_correction='H'  # High error correction
        )
        
        FIRSQRCodeGenerator.generate_qr_code_to_file(
            test_invoice,
            test_irn,
            str(custom_output),
            custom_options
        )
        
        if custom_output.exists():
            print(f"\n✅ Custom options QR saved!")
            print(f"   File: {custom_output}")
            print(f"   Size: {custom_output.stat().st_size} bytes")
            print(f"   Options: box_size=15, border=6, error_correction=H")
            
    except Exception as e:
        print(f"❌ Error with custom QR: {e}")
    
    # Save metadata with timestamp
    metadata = {
        "test_irn": test_irn,
        "timestamp": timestamp,
        "full_timestamp": datetime.now().isoformat(),
        "files_created": {
            "main_qr": {
                "path": str(output_path),
                "exists": output_path.exists(),
                "size": output_path.stat().st_size if output_path.exists() else 0
            },
            "simple_qr": {
                "path": str(simple_output),
                "exists": simple_output.exists(), 
                "size": simple_output.stat().st_size if simple_output.exists() else 0
            },
            "custom_qr": {
                "path": str(custom_output),
                "exists": custom_output.exists(),
                "size": custom_output.stat().st_size if custom_output.exists() else 0
            }
        }
    }
    
    metadata_path = output_dir / f"python_qr_metadata_{timestamp}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n📊 Metadata saved to: {metadata_path}")
    print(f"\n✅ Test complete! All files timestamped with: {timestamp}")
    print(f"📁 Check 'qr_output' directory for PNG files")
    
    # List all generated files for this run
    print(f"\n📋 Files generated in this run:")
    for file_type, file_info in metadata['files_created'].items():
        if file_info['exists']:
            print(f"   - {Path(file_info['path']).name} ({file_info['size']} bytes)")

if __name__ == "__main__":
    test_python_qr_save()