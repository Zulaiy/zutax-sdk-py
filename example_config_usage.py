#!/usr/bin/env python3
"""Example: FIRS signing and QR generation use config instead of os.environ."""

from zutax import ZutaxClient, ZutaxConfig
from zutax.crypto.irn import IRNGenerator
from zutax.crypto.firs_qrcode import FIRSQRCodeGenerator
from zutax.crypto.firs_signing import FIRSSigner

# Configuration now holds all the FIRS keys and settings
config = ZutaxConfig(
    api_key="your-api-key",
    api_secret="your-api-secret",
    business_id="TEST-BUS",
    business_name="Test Business",
    tin="12345678901",
    service_id="TESTSERV",  # Replaces FIRS_SERVICE_ID env var
    firs_public_key="base64-encoded-public-key",  # Replaces FIRS_PUBLIC_KEY
    firs_certificate="base64-encoded-certificate",  # Replaces FIRS_CERTIFICATE
)

# Now all components use the config object

# 1. IRN Generation with config
irn_generator = IRNGenerator(config=config)
# Service ID will be taken from config.service_id instead of os.environ

# 2. QR Code Generation with config
qr_generator = FIRSQRCodeGenerator(config=config)
# FIRS keys will be taken from config instead of os.environ

# 3. FIRS Signing with config
signer = FIRSSigner(config=config)
# Public key and certificate from config instead of os.environ

# 4. Client automatically passes config to all components
client = ZutaxClient(config=config)
# When client generates IRN or QR codes, it passes config automatically

print("✅ Configuration-based approach:")
print(f"- Service ID from config: {config.service_id}")
print(f"- FIRS keys configured: {config.firs_public_key is not None}")
print("- No more os.environ dependency for FIRS operations!")

# Fallback behavior still works:
# If config doesn't have values, it will check os.environ as fallback
# If neither has values, it will generate defaults (for service_id)
# or raise errors (for keys)