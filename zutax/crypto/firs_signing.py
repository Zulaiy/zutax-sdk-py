"""FIRS digital signing implementation (Zutax native).

This module mirrors the legacy behavior but keeps heavy Crypto imports lazy,
so importing zutax.crypto remains light unless signing is used.
"""

from __future__ import annotations

import os
import json
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel


class FIRSSigningPayload(BaseModel):
    """FIRS signing payload structure."""

    irn: str
    certificate: str


class FIRSEncryptionResult(BaseModel):
    """FIRS encryption result."""

    encrypted_base64: str
    timestamp: int


class FIRSSigningResult(BaseModel):
    """FIRS signing result."""

    encrypted_data: str
    encryption_result: FIRSEncryptionResult
    timestamp: int
    irn_with_timestamp: str


class FIRSSigner:
    """FIRS digital signing implementation with lazy Crypto imports."""

    def __init__(self) -> None:
        self.firs_public_key_pem: Optional[str] = None
        self.firs_certificate: Optional[str] = None
        self._load_firs_keys()

    def _ensure_crypto(self):  # pragma: no cover - trivial import helper
        """Import Crypto only when needed to avoid import-time errors."""
        try:
            from Crypto.PublicKey import RSA  # type: ignore
            from Crypto.Cipher import PKCS1_v1_5  # type: ignore
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "pycryptodome (Crypto) is required for signing operations"
            ) from exc
        return RSA, PKCS1_v1_5

    def _load_firs_keys(self) -> None:
        """Load FIRS public key and certificate from env or key file."""
        try:
            # First try environment variables
            public_key_text = os.environ.get("FIRS_PUBLIC_KEY")
            certificate_text = os.environ.get("FIRS_CERTIFICATE")

            if public_key_text and certificate_text:
                # FIRS_PUBLIC_KEY is Base64-encoded PEM
                public_key_pem = base64.b64decode(
                    public_key_text
                ).decode("utf-8")
                # FIRS_CERTIFICATE is Base64-encoded certificate data
                certificate_base64 = certificate_text

                self.firs_public_key_pem = public_key_pem
                self.firs_certificate = certificate_base64
                return

            # Fallback: try to load from key file (same relative path
            # as legacy)
            key_file_path = (
                Path(
                    (
                        "../../FIRS_e-invoice-"
                        "ZULAIY TECHNOLOGIES LTD_cryptographic_key.txt"
                    )
                )
                .resolve()
            )
            if key_file_path.exists():
                with open(key_file_path, "r", encoding="utf-8") as f:
                    keys_json = json.load(f)

                public_key_pem = base64.b64decode(
                    keys_json["public_key"]
                ).decode("utf-8")
                certificate_base64 = keys_json["certificate"]

                self.firs_public_key_pem = public_key_pem
                self.firs_certificate = certificate_base64
                return
        except Exception:  # noqa: BLE001
            # Defer error until use
            pass

    def sign_irn(
        self, irn: str, timestamp: Optional[int] = None
    ) -> FIRSSigningResult:
        """
        Sign IRN according to FIRS specification using RSA-PKCS1 v1_5.
    Creates payload with IRN.timestamp and certificate, encrypts with
    public key.
        Returns base64-encoded ciphertext, timestamp, and IRN with timestamp.
        """
        ts = timestamp or int(time.time())
        irn_with_timestamp = f"{irn}.{ts}"

        payload = FIRSSigningPayload(
            irn=irn_with_timestamp, certificate=self.firs_certificate or ""
        )

        encryption_result = self._encrypt_payload(payload)

        return FIRSSigningResult(
            encrypted_data=encryption_result.encrypted_base64,
            encryption_result=encryption_result,
            timestamp=ts,
            irn_with_timestamp=irn_with_timestamp,
        )

    def _encrypt_payload(
        self, payload: FIRSSigningPayload
    ) -> FIRSEncryptionResult:
        """Encrypt payload using RSA-PKCS1 v1_5, matching legacy behavior."""
        if not self.firs_public_key_pem or not self.firs_certificate:
            raise RuntimeError(
                "FIRS public key and certificate must be loaded before"
                " encryption"
            )

        RSA, PKCS1_v1_5 = self._ensure_crypto()

        try:
            payload_reduced = {
                "irn": payload.irn,
                "certificate": payload.certificate,
            }

            rsa_key = RSA.import_key(self.firs_public_key_pem)
            cipher = PKCS1_v1_5.new(rsa_key)

            data_bytes_reduced = json.dumps(payload_reduced).encode("utf-8")
            encrypted_data_reduced = cipher.encrypt(data_bytes_reduced)

            encrypted_base64 = base64.b64encode(encrypted_data_reduced).decode(
                "utf-8"
            )

            return FIRSEncryptionResult(
                encrypted_base64=encrypted_base64,
                timestamp=int(time.time() * 1000),  # ms
            )
        except Exception as error:  # noqa: BLE001
            raise RuntimeError(f"FIRS encryption failed: {error}") from error

    @staticmethod
    def decode_public_key(base64_key: str) -> str:
        """Decode and verify FIRS public key."""
        try:
            return base64.b64decode(base64_key).decode("utf-8")
        except Exception as error:  # noqa: BLE001
            raise ValueError(
                f"Failed to decode public key: {error}"
            ) from error

    @staticmethod
    def create_qr_data(encrypted_data: str) -> str:
        """Create QR code data from encrypted payload (identity)."""
        return encrypted_data

    @staticmethod
    def encrypt_for_qr(
        irn: str, certificate: str, public_key_input: str
    ) -> str:
        """
        Convenience method mirroring legacy: IRN.timestamp + certificate,
    decode public key (base64 PEM or raw PEM), RSA-PKCS1 v1_5 encrypt,
    base64.
        """
        RSA, PKCS1_v1_5 = FIRSSigner()._ensure_crypto()
        try:
            timestamp = int(time.time())
            irn_with_timestamp = f"{irn}.{timestamp}"

            payload_reduced = {
                "irn": irn_with_timestamp,
                "certificate": certificate,
            }

            if "-----BEGIN PUBLIC KEY-----" in public_key_input:
                public_key_pem = public_key_input
            else:
                public_key_pem = base64.b64decode(public_key_input).decode(
                    "utf-8"
                )

            rsa_key = RSA.import_key(public_key_pem)
            cipher = PKCS1_v1_5.new(rsa_key)

            data_bytes_reduced = json.dumps(payload_reduced).encode("utf-8")
            encrypted_data_reduced = cipher.encrypt(data_bytes_reduced)

            encrypted_b64_reduced = base64.b64encode(
                encrypted_data_reduced
            ).decode("utf-8")

            return encrypted_b64_reduced
        except Exception as error:  # noqa: BLE001
            raise RuntimeError(
                f"Failed to encrypt for QR code: {error}"
            ) from error

    def get_public_key_pem(self) -> Optional[str]:
        """Get the loaded FIRS public key in PEM format."""
        return self.firs_public_key_pem

    def get_certificate(self) -> Optional[str]:
        """Get the FIRS certificate."""
        return self.firs_certificate

    def is_configured(self) -> bool:
        """Check if the signer is properly configured with FIRS keys."""
        return bool(self.firs_public_key_pem and self.firs_certificate)

    def demonstrate_signing_flow(self, irn: str) -> Dict[str, Any]:
        """
        Demonstrate the complete FIRS signing flow according to specification.
        Returns all intermediate steps for verification.
        """
        timestamp = int(time.time())
        irn_with_timestamp = f"{irn}.{timestamp}"

        payload = FIRSSigningPayload(
            irn=irn_with_timestamp, certificate=self.firs_certificate or ""
        )
        payload_json = payload.model_dump_json()
        encryption_result = self._encrypt_payload(payload)

        return {
            "base_irn": irn,
            "timestamp": timestamp,
            "irn_with_timestamp": irn_with_timestamp,
            "payload": payload.model_dump(),
            "payload_json": payload_json,
            "encrypted_data": encryption_result.encrypted_base64,
            "qr_code_ready": len(encryption_result.encrypted_base64) > 0,
        }
