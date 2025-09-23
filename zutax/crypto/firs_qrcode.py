"""FIRS QR code generation utilities (Zutax native)."""

import base64
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

import qrcode
from pydantic import BaseModel
from qrcode.image.pil import PilImage

from .irn import IRNGenerator


class FIRSQRCodeOptions(BaseModel):
    """QR code generation options."""

    version: Optional[int] = None  # Auto-detect
    error_correction: str = "M"  # Match JavaScript default
    box_size: int = 10
    border: int = 4
    fill_color: str = "black"
    back_color: str = "white"
    business_info: Optional[Dict[str, str]] = None
    custom_content: Optional[Dict[str, Any]] = None
    customization: Optional[Dict[str, Any]] = None


class FIRSQRCodeGenerator:
    """FIRS-compliant QR code generator."""

    def __init__(self, config: Optional[Any] = None):
        """Initialize with optional config."""
        self.config = config

    def generate_qr_code(
        self,
        irn: str,
        options: Optional[FIRSQRCodeOptions] = None,
    ) -> str:
        """Generate QR for IRN and return base64 PNG data."""
        if options is None:
            options = FIRSQRCodeOptions()

        # Import signer lazily to avoid heavy dependency at import time
        from .firs_signing import FIRSSigner  # noqa: WPS433

        signer = FIRSSigner(config=self.config)
        if not signer.is_configured():
            raise Exception(
                "FIRS keys not configured. Cannot generate QR code."
            )

        # Sign the IRN to get encrypted data
        signing_result = signer.sign_irn(irn)
        qr_data = signing_result.encrypted_data

        # Generate QR code
        qr_code = self._create_qr_code(qr_data, options)

        # Convert to base64 PNG
        img_buffer = io.BytesIO()
        qr_code.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        img_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        return img_base64

    def generate_qr_code_to_file(
        self,
        invoice: Any,
        irn: str,
        file_path: str,
        options: Optional[FIRSQRCodeOptions] = None,
    ) -> None:
        """Generate FIRS QR code and save to file."""
        if options is None:
            options = FIRSQRCodeOptions()

        # Import signer lazily to avoid heavy dependency at import time
        from .firs_signing import FIRSSigner  # noqa: WPS433

        signer = FIRSSigner(config=self.config)
        if not signer.is_configured():
            raise Exception(
                "FIRS keys not configured. Cannot generate QR code."
            )

        # Sign the IRN to get encrypted data
        signing_result = signer.sign_irn(irn)
        qr_data = signing_result.encrypted_data

        # Generate QR code
        qr_code = self._create_qr_code(qr_data, options)

        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        qr_code.save(file_path, format="PNG")

    def _create_qr_code(
        self,
        data: str,
        options: FIRSQRCodeOptions,
    ) -> PilImage:
        """Create QR code image from data."""
        # Map error correction levels
        error_correction_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

        error_correction = error_correction_map.get(
            options.error_correction,
            qrcode.constants.ERROR_CORRECT_M,
        )

        # Create QR code with settings
        qr = qrcode.QRCode(
            version=options.version,
            error_correction=error_correction,
            box_size=options.box_size,
            border=options.border,
        )

        qr.add_data(data)
        qr.make(fit=True)

        # Create image with provided colors (match legacy defaults)
        img = qr.make_image(
            fill_color=options.fill_color,
            back_color=options.back_color,
        )
        return img

    def generate_multiple_qr_codes(
        self,
        invoices: List[Any],
        output_dir: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate QR codes for multiple invoices."""
        results: List[Dict[str, Any]] = []

        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        for i, invoice in enumerate(invoices):
            try:
                # Generate IRN if not present
                if not getattr(invoice, "irn", None):
                    irn_generator = IRNGenerator(config=self.config)
                    irn = irn_generator.generate_irn(invoice)
                else:
                    irn = invoice.irn

                if output_dir:
                    output_path = Path(output_dir) / f"qr_{irn}_{i + 1}.png"
                    self.generate_qr_code_to_file(
                        invoice,
                        irn,
                        str(output_path),
                    )
                    result: Dict[str, Any] = {
                        "irn": irn,
                        "file_path": str(output_path),
                        "success": True,
                    }
                else:
                    qr_base64 = self.generate_qr_code(irn)
                    result = {
                        "irn": irn,
                        "qr_code": qr_base64,
                        "success": True,
                    }

                results.append(result)

            except Exception as error:  # noqa: BLE001
                results.append(
                    {
                        "irn": getattr(invoice, "irn", f"invoice_{i + 1}"),
                        "error": str(error),
                        "success": False,
                    }
                )

        return results

    @staticmethod
    def validate_qr_data(qr_data: str) -> bool:
        """Validate QR code data format (base64)."""
        try:
            base64.b64decode(qr_data)
            return True
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def extract_qr_info(qr_data: str) -> Dict[str, Any]:
        """Extract information from QR code data (for debugging)."""
        return {
            "data_length": len(qr_data),
            "is_base64": FIRSQRCodeGenerator.validate_qr_data(qr_data),
            "data_preview": (
                qr_data[:50] + "..." if len(qr_data) > 50 else qr_data
            ),
        }
