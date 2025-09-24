"""IRN (Invoice Reference Number) generation utilities (native Zutax).

Provides a simple, FIRS-compatible IRN generator with helpers for
validation and parsing. This replaces the legacy proxy.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..models.invoice import Invoice


class IRNGenerator:
    """Generates FIRS-compliant Invoice Reference Numbers (IRN).

    Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
    Example: INV001-94ND90NR-20240611
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize with optional config."""
        self.config = config

    def generate_irn(self, invoice: "Invoice" | str) -> str:
        """
        Generate IRN according to FIRS specification.
        Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
        Note: InvoiceNumber may itself contain dashes.
        """

        # Extract invoice number
        if isinstance(invoice, str):
            invoice_number = invoice
        elif hasattr(invoice, "invoice_number"):
            invoice_number = getattr(invoice, "invoice_number", None)
        else:
            raise TypeError("invoice must be an Invoice instance or a string", invoice)
    
        # Prefer service ID from config, then env
        service_id = None
        if self.config:
            service_id = getattr(self.config, "service_id", None)
        if not service_id:
            service_id = os.environ.get("FIRS_SERVICE_ID")
        if not service_id:
            raise ValueError(
                "Service ID not found in config or FIRS_SERVICE_ID env var"
            )
        # Date stamp from invoice.issue_date if available; else now
        issue_date = getattr(invoice, "issue_date", None)
        date_stamp = self._generate_date_stamp(issue_date)

        return f"{invoice_number}-{service_id}-{date_stamp}"

    @staticmethod
    def _generate_service_id() -> str:
        """Generate 8-character service ID using UUID4 base."""
        uuid_str = str(uuid.uuid4()).replace("-", "").upper()
        return uuid_str[:8]

    @staticmethod
    def _generate_date_stamp(issue_date: Optional[datetime] = None) -> str:
        """Generate date stamp in YYYYMMDD format."""
        dt = issue_date or datetime.now()
        return dt.strftime("%Y%m%d")

    @staticmethod
    def validate_irn(irn: str) -> bool:
        """Validate IRN format.
        Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
        Note: InvoiceNumber may contain dashes.
        """
        if not irn:
            return False

        parts = irn.split("-")
        if len(parts) < 3:
            return False

        date_stamp = parts[-1]
        service_id = parts[-2]
        invoice_number = "-".join(parts[:-2])

        if not invoice_number:
            return False
        if len(service_id) != 8 or not service_id.isalnum():
            return False
        if len(date_stamp) != 8 or not date_stamp.isdigit():
            return False
        try:
            datetime.strptime(date_stamp, "%Y%m%d")
        except ValueError:
            return False
        return True

    @staticmethod
    def extract_components(irn: str) -> Dict[str, object]:
        """Extract components from IRN as a dict.
        Raises ValueError if the IRN is invalid.
        """
        if not IRNGenerator.validate_irn(irn):
            raise ValueError("Invalid IRN format")

        parts = irn.split("-")
        date_stamp = parts[-1]
        service_id = parts[-2]
        invoice_number = "-".join(parts[:-2])
        issue_date = datetime.strptime(date_stamp, "%Y%m%d")

        return {
            "invoice_number": invoice_number,
            "service_id": service_id,
            "date_stamp": date_stamp,
            "issue_date": issue_date,
        }

    @staticmethod
    def create_custom_irn(
        invoice_number: str,
        service_id: Optional[str] = None,
        issue_date: Optional[datetime] = None,
    ) -> str:
        """Create custom IRN with specific components."""
        sid = (service_id or IRNGenerator._generate_service_id())[:8].upper()
        ds = IRNGenerator._generate_date_stamp(issue_date)
        irn = f"{invoice_number}-{sid}-{ds}"
        if not IRNGenerator.validate_irn(irn):
            raise ValueError("Generated IRN is invalid")
        return irn



__all__ = ["IRNGenerator"]
