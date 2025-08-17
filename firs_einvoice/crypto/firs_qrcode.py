
"""FIRS QR code generation utilities."""

import base64
from pathlib import Path
from typing import Optional, Dict, Any, Union
import qrcode
from qrcode.image.pil import PilImage
import io
from pydantic import BaseModel

from .firs_signing import FIRSSigner
from .irn import IRNGenerator


class FIRSQRCodeOptions(BaseModel):
    """QR code generation options."""
    version: Optional[int] = None  # Auto-detect as in working code
    error_correction: str = 'H'  # Use high error correction as in working code
    box_size: int = 10
    border: int = 4
    fill_color: str = 'black'
    back_color: str = 'white'
    business_info: Optional[Dict[str, str]] = None
    custom_content: Optional[Dict[str, Any]] = None
    customization: Optional[Dict[str, Any]] = None


class FIRSQRCodeGenerator:
    """FIRS-compliant QR code generator."""
    
    @staticmethod
    def generate_qr_code(invoice, irn: str, options: Optional[FIRSQRCodeOptions] = None) -> str:
        """
        Generate FIRS-compliant QR code for invoice.
        Returns base64-encoded PNG image.
        """
        if options is None:
            options = FIRSQRCodeOptions()
        
        # Get encrypted data for QR code
        signer = FIRSSigner()
        if not signer.is_configured():
            raise Exception("FIRS keys not configured. Cannot generate QR code.")
        
        # Sign the IRN to get encrypted data
        signing_result = signer.sign_irn(irn)
        qr_data = signing_result.encrypted_data
        
        # Generate QR code
        qr_code = FIRSQRCodeGenerator._create_qr_code(qr_data, options)
        
        # Convert to base64 PNG
        img_buffer = io.BytesIO()
        qr_code.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return img_base64
    
    @staticmethod
    async def generate_qr_code_to_file(invoice, irn: str, file_path: str, 
                                     options: Optional[FIRSQRCodeOptions] = None) -> None:
        """
        Generate FIRS-compliant QR code and save to file.
        """
        if options is None:
            options = FIRSQRCodeOptions()
        
        # Get encrypted data for QR code
        signer = FIRSSigner()
        if not signer.is_configured():
            raise Exception("FIRS keys not configured. Cannot generate QR code.")
        
        # Sign the IRN to get encrypted data
        signing_result = signer.sign_irn(irn)
        qr_data = signing_result.encrypted_data
        
        # Generate QR code
        qr_code = FIRSQRCodeGenerator._create_qr_code(qr_data, options)
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        qr_code.save(file_path)
        print(f"✓ QR code saved to: {file_path}")
    
    @staticmethod
    def _create_qr_code(data: str, options: FIRSQRCodeOptions) -> PilImage:
        """Create QR code image from data."""
        # Map error correction levels
        error_correction_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        error_correction = error_correction_map.get(options.error_correction, 
                                                  qrcode.constants.ERROR_CORRECT_H)
        
        # Create QR code with settings matching working implementation
        qr = qrcode.QRCode(
            version=options.version,  # Use None for auto-detect as in working code
            error_correction=error_correction,
            box_size=options.box_size,
            border=options.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image with exact settings from working code
        img = qr.make_image(
            fill="black",  # Match working code exactly
            back_color="white"  # Match working code exactly
        )
        
        return img
    
    @staticmethod
    def generate_simple_qr(irn: str, certificate: str, public_key: str, 
                          output_path: Optional[str] = None) -> Union[str, None]:
        """
        Generate simple QR code with direct encryption.
        Returns base64 image data if no output_path, otherwise saves to file.
        """
        try:
            # Encrypt data
            encrypted_data = FIRSSigner.encrypt_for_qr(irn, certificate, public_key)
            
            # Create QR code
            options = FIRSQRCodeOptions()
            qr_code = FIRSQRCodeGenerator._create_qr_code(encrypted_data, options)
            
            if output_path:
                # Save to file
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                qr_code.save(output_path)
                print(f"✓ QR code saved to: {output_path}")
                return None
            else:
                # Return base64
                img_buffer = io.BytesIO()
                qr_code.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                return img_base64
                
        except Exception as error:
            raise Exception(f"Failed to generate QR code: {error}")
    
    @staticmethod
    def generate_multiple_qr_codes(invoices: list, output_dir: str = None) -> list:
        """Generate QR codes for multiple invoices."""
        results = []
        
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, invoice in enumerate(invoices):
            try:
                # Generate IRN if not present
                irn = getattr(invoice, 'irn', None) or IRNGenerator.generate_irn(invoice)
                
                if output_dir:
                    output_path = Path(output_dir) / f"qr_{irn}_{i+1}.png"
                    FIRSQRCodeGenerator.generate_qr_code_to_file(invoice, irn, str(output_path))
                    result = {
                        'irn': irn,
                        'file_path': str(output_path),
                        'success': True
                    }
                else:
                    qr_base64 = FIRSQRCodeGenerator.generate_qr_code(invoice, irn)
                    result = {
                        'irn': irn,
                        'qr_code': qr_base64,
                        'success': True
                    }
                
                results.append(result)
                
            except Exception as error:
                results.append({
                    'irn': getattr(invoice, 'irn', f'invoice_{i+1}'),
                    'error': str(error),
                    'success': False
                })
        
        return results
    
    @staticmethod
    def validate_qr_data(qr_data: str) -> bool:
        """Validate QR code data format."""
        try:
            # Should be valid base64
            base64.b64decode(qr_data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def extract_qr_info(qr_data: str) -> Dict[str, Any]:
        """Extract information from QR code data (for debugging)."""
        return {
            'data_length': len(qr_data),
            'is_base64': FIRSQRCodeGenerator.validate_qr_data(qr_data),
            'data_preview': qr_data[:50] + '...' if len(qr_data) > 50 else qr_data
        }