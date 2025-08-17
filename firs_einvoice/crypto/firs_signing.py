"""FIRS digital signing implementation."""

import os
import json
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
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
    """FIRS digital signing implementation."""
    
    def __init__(self):
        self.firs_public_key: Optional[RSA.RsaKey] = None
        self.firs_certificate: Optional[str] = None
        self._load_firs_keys()
    
    def _load_firs_keys(self) -> None:
        """Load FIRS public key and certificate from environment variables or key file."""
        try:
            # First try environment variables
            public_key_text = os.environ.get('FIRS_PUBLIC_KEY')
            certificate_text = os.environ.get('FIRS_CERTIFICATE')
            
            if public_key_text and certificate_text:
                # FIRS_PUBLIC_KEY is Base64-encoded PEM, so decode it first
                public_key_pem = base64.b64decode(public_key_text).decode('utf-8')
                # FIRS_CERTIFICATE is Base64-encoded certificate data
                certificate_base64 = certificate_text
                
                self.firs_public_key = RSA.import_key(public_key_pem)
                self.firs_certificate = certificate_base64
                print('✓ FIRS crypto keys loaded from environment variables')
                return
            
            # Fallback: try to load from key file
            key_file_path = Path('../../FIRS_e-invoice-ZULAIY TECHNOLOGIES LTD_cryptographic_key.txt').resolve()
            if key_file_path.exists():
                with open(key_file_path, 'r') as f:
                    keys_json = json.load(f)
                
                public_key_pem = base64.b64decode(keys_json['public_key']).decode('utf-8')
                certificate_base64 = keys_json['certificate']
                
                self.firs_public_key = RSA.import_key(public_key_pem)
                self.firs_certificate = certificate_base64
                print('✓ FIRS crypto keys loaded from key file')
                return
            
            raise Exception('FIRS keys not found. Set FIRS_PUBLIC_KEY and FIRS_CERTIFICATE environment variables or ensure key file exists.')
            
        except Exception as error:
            print(f'Failed to load FIRS keys: {error}')
            print('   Make sure your keys are in the correct Base64 format')
    
    def sign_irn(self, irn: str, timestamp: Optional[int] = None) -> FIRSSigningResult:
        """
        Sign IRN according to FIRS specification.
        Creates payload with IRN.timestamp and certificate, then encrypts with public key.
        Format: "IRN.UnixTimestamp" as per FIRS documentation.
        """
        ts = timestamp or int(time.time())
        irn_with_timestamp = f"{irn}.{ts}"
        
        # Create payload according to FIRS specification
        # Must be JSON with both irn (including timestamp) and certificate
        payload = FIRSSigningPayload(
            irn=irn_with_timestamp,
            certificate=self.firs_certificate or ''
        )
        
        # Encrypt the payload using RSA encryption
        encryption_result = self._encrypt_payload(payload)
        
        return FIRSSigningResult(
            encrypted_data=encryption_result.encrypted_base64,
            encryption_result=encryption_result,
            timestamp=ts,
            irn_with_timestamp=irn_with_timestamp
        )
    
    def _encrypt_payload(self, payload: FIRSSigningPayload) -> FIRSEncryptionResult:
        """
        Encrypt payload using RSA encryption as per FIRS specification.
        According to FIRS spec: JSON payload with IRN.timestamp and certificate
        Uses RSA-PKCS1 padding to match the working implementation.
        """
        if not self.firs_public_key or not self.firs_certificate:
            raise Exception('FIRS public key and certificate must be loaded before encryption')
        
        try:
            # Create reduced payload as per working implementation
            payload_reduced = {
                "irn": payload.irn,
                "certificate": payload.certificate
            }
            
            print("✅ Reduced payload:", payload_reduced)
            
            # Create cipher using PyCrypto/PyCryptodome (matches working code)
            cipher = PKCS1_v1_5.new(self.firs_public_key)
            
            # Encrypt the reduced payload
            data_bytes_reduced = json.dumps(payload_reduced).encode("utf-8")
            encrypted_data_reduced = cipher.encrypt(data_bytes_reduced)
            
            # Convert to Base64 for QR code as per FIRS specification
            encrypted_base64 = base64.b64encode(encrypted_data_reduced).decode('utf-8')
            
            print('✓ Payload encrypted using FIRS RSA encryption (PKCS1)')
            return FIRSEncryptionResult(
                encrypted_base64=encrypted_base64,
                timestamp=int(time.time() * 1000)  # Milliseconds
            )
            
        except Exception as error:
            print(f'Failed to encrypt payload with FIRS RSA encryption: {error}')
            raise Exception(f'FIRS encryption failed: {error}')
    
    @staticmethod
    def decode_public_key(base64_key: str) -> str:
        """Decode and verify FIRS public key."""
        try:
            return base64.b64decode(base64_key).decode('utf-8')
        except Exception as error:
            raise Exception(f'Failed to decode public key: {error}')
    
    @staticmethod
    def create_qr_data(encrypted_data: str) -> str:
        """
        Create QR code data from encrypted payload.
        As per FIRS specification, QR code contains only the Base64 encrypted data.
        """
        return encrypted_data
    
    @staticmethod
    def encrypt_for_qr(irn: str, certificate: str, public_key_input: str) -> str:
        """
        Simple method to encrypt IRN and certificate following FIRS documentation exactly.
        This matches the workflow described in the FIRS documentation.
        """
        try:
            # Step 1: Add timestamp to IRN (FIRS requirement)
            timestamp = int(time.time())
            irn_with_timestamp = f"{irn}.{timestamp}"
            
            # Step 2: Create reduced payload as per working implementation
            payload_reduced = {
                'irn': irn_with_timestamp,
                'certificate': certificate
            }
            
            print("✅ Reduced payload:", payload_reduced)
            
            # Step 3: Handle public key input - could be Base64-encoded PEM or direct PEM
            if '-----BEGIN PUBLIC KEY-----' in public_key_input:
                # Already in PEM format
                public_key_pem = public_key_input
            else:
                # Assume it's Base64-encoded PEM, decode it
                public_key_pem = base64.b64decode(public_key_input).decode('utf-8')
            
            # Step 4: Load public key using PyCrypto/PyCryptodome
            rsa_key = RSA.import_key(public_key_pem)
            cipher = PKCS1_v1_5.new(rsa_key)
            
            # Step 5: Encrypt the reduced payload
            data_bytes_reduced = json.dumps(payload_reduced).encode("utf-8")
            encrypted_data_reduced = cipher.encrypt(data_bytes_reduced)
            
            # Step 6: Convert to Base64 for QR code
            encrypted_b64_reduced = base64.b64encode(encrypted_data_reduced).decode("utf-8")
            
            return encrypted_b64_reduced
            
        except Exception as error:
            raise Exception(f'Failed to encrypt for QR code: {error}')
    
    @staticmethod
    def is_valid_base64(s: str) -> bool:
        """Validate if a string is properly base64 encoded."""
        try:
            return base64.b64encode(base64.b64decode(s)).decode() == s
        except Exception:
            return False
    
    def get_public_key_pem(self) -> Optional[str]:
        """Get the loaded FIRS public key in PEM format."""
        if not self.firs_public_key:
            return None
        
        return self.firs_public_key.export_key(format='PEM').decode('utf-8')
    
    def get_certificate(self) -> Optional[str]:
        """Get the FIRS certificate."""
        return self.firs_certificate
    
    def is_configured(self) -> bool:
        """Check if the signer is properly configured with FIRS keys."""
        return bool(self.firs_public_key and self.firs_certificate)
    
    def demonstrate_signing_flow(self, irn: str) -> Dict[str, Any]:
        """
        Demonstrate the complete FIRS signing flow according to specification.
        Returns all intermediate steps for verification.
        """
        timestamp = int(time.time())
        
        payload = FIRSSigningPayload(
            irn=irn,
            certificate=self.firs_certificate or ''
        )
        
        payload_json = payload.model_dump_json()
        encryption_result = self._encrypt_payload(payload)
        
        return {
            'base_irn': irn,
            'timestamp': timestamp,
            'irn_with_timestamp': irn,
            'payload': payload.model_dump(),
            'payload_json': payload_json,
            'encrypted_data': encryption_result.encrypted_base64,
            'qr_code_ready': len(encryption_result.encrypted_base64) > 0
        }