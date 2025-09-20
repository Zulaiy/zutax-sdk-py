"""Minimal QR code generation test.

This test configures in-memory FIRS keys, generates an IRN-like string,
produces a base64 PNG QR code using FIRSQRCodeGenerator.generate_qr_code(irn),
and asserts that the output is valid base64 and decodes to PNG bytes.
"""

import base64
import os
from pathlib import Path
from dotenv import load_dotenv

import pytest
from zutax.crypto.firs_qrcode import FIRSQRCodeGenerator
import uuid


# Environment must provide test keys via FIRS_PUBLIC_KEY (base64 PEM)
# and FIRS_CERTIFICATE. If missing, the test will be skipped.


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

# Load environment variables from .env, if present
load_dotenv()


def _ensure_test_keys():
    # Expect env vars to be set by CI or developer; if not, skip.
    pub = os.environ.get("FIRS_PUBLIC_KEY")
    cert = os.environ.get("FIRS_CERTIFICATE")
    if not (pub and cert):
        pytest.skip(
            "Missing FIRS_PUBLIC_KEY/FIRS_CERTIFICATE; skipping QR test"
        )


@pytest.mark.qr_unit
def test_generate_qr_base64_is_png():
    _ensure_test_keys()
    try:
        import Crypto  # noqa: F401
    except Exception:
        pytest.skip("pycryptodome (Crypto) not installed; skipping QR test")


    irn = f"INV-TEST-{uuid.uuid4().hex[:8].upper()}-UNIT"

    # Generate base64 PNG via the maintained API
    b64_png = FIRSQRCodeGenerator.generate_qr_code(irn)
    assert isinstance(b64_png, str)
    assert len(b64_png) > 0

    # Validate base64 and PNG signature
    raw = base64.b64decode(b64_png)
    assert raw.startswith(PNG_MAGIC)

    # Optionally write to tmp for local debugging
    out = Path(__file__).parent / "qr_output"
    out.mkdir(parents=True, exist_ok=True)
    (out / "unit_simple_qr.png").write_bytes(raw)
