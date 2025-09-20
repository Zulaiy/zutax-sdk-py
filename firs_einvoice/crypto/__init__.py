"""FIRS cryptographic operations.

This module uses lazy imports to avoid heavy crypto dependencies
at import time.
"""


def __getattr__(name):  # pragma: no cover
    if name in {
        "FIRSSigner",
        "FIRSSigningPayload",
        "FIRSSigningResult",
        "FIRSEncryptionResult",
    }:
        from . import firs_signing as _sign

        mapping = {
            "FIRSSigner": _sign.FIRSSigner,
            "FIRSSigningPayload": _sign.FIRSSigningPayload,
            "FIRSSigningResult": _sign.FIRSSigningResult,
            "FIRSEncryptionResult": _sign.FIRSEncryptionResult,
        }
        return mapping[name]

    if name in {"FIRSQRCodeGenerator", "FIRSQRCodeOptions"}:
        from . import firs_qrcode as _qr

        mapping = {
            "FIRSQRCodeGenerator": _qr.FIRSQRCodeGenerator,
            "FIRSQRCodeOptions": _qr.FIRSQRCodeOptions,
        }
        return mapping[name]

    if name == "IRNGenerator":
        from .irn import IRNGenerator

        return IRNGenerator
    raise AttributeError(name)


__all__ = [
    "FIRSSigner",
    "FIRSSigningPayload",
    "FIRSSigningResult",
    "FIRSEncryptionResult",
    "FIRSQRCodeGenerator",
    "FIRSQRCodeOptions",
    "IRNGenerator",
]
