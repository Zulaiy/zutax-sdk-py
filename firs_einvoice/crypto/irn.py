"""IRN (Invoice Reference Number) generation utilities."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.invoice import Invoice


class IRNGenerator:
    """Generates FIRS-compliant Invoice Reference Numbers (IRN)."""
    
    @staticmethod
    def generate_irn(invoice: 'Invoice') -> str:
        """
        Generate IRN according to FIRS specification.
        Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
        Example: INV001-94ND90NR-20240611
        """
        import os
        
        # Extract invoice number (remove any prefix characters)
        invoice_number = invoice.invoice_number or "INV001"
        
        # Use FIRS-assigned service ID from environment
        service_id = os.environ.get('FIRS_SERVICE_ID')
        if not service_id:
            # Only generate if not provided
            service_id = IRNGenerator._generate_service_id()
        
        # Ensure exactly 8 characters
        service_id = service_id[:8].upper()
        
        # Generate date stamp from invoice issue date
        date_stamp = IRNGenerator._generate_date_stamp(invoice.issue_date if hasattr(invoice, 'issue_date') else None)
        
        # Combine components
        irn = f"{invoice_number}-{service_id}-{date_stamp}"
        
        return irn
    
    @staticmethod
    def _generate_service_id() -> str:
        """Generate 8-character service ID."""
        # Use UUID4 and extract 8 characters
        uuid_str = str(uuid.uuid4()).replace('-', '').upper()
        return uuid_str[:8]
    
    @staticmethod
    def _generate_date_stamp(issue_date: datetime = None) -> str:
        """Generate date stamp in YYYYMMDD format."""
        if issue_date is None:
            issue_date = datetime.now()
        
        return issue_date.strftime("%Y%m%d")
    
    @staticmethod
    def validate_irn(irn: str) -> bool:
        """Validate IRN format.
        Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
        Note: InvoiceNumber may contain dashes
        """
        if not irn:
            return False
        
        parts = irn.split('-')
        if len(parts) < 3:
            return False
        
        # Last part should be date stamp (8 digits)
        date_stamp = parts[-1]
        # Second to last should be service ID (8 alphanumeric)
        service_id = parts[-2]
        # Everything else is the invoice number
        invoice_number = '-'.join(parts[:-2])
        
        # Validate components
        if not invoice_number:
            return False
        
        if len(service_id) != 8 or not service_id.isalnum():
            return False
        
        if len(date_stamp) != 8 or not date_stamp.isdigit():
            return False
        
        # Validate date format
        try:
            datetime.strptime(date_stamp, "%Y%m%d")
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def extract_components(irn: str) -> dict:
        """Extract components from IRN.
        Format: {InvoiceNumber}-{ServiceID}-{DateStamp}
        Note: InvoiceNumber may contain dashes
        """
        if not IRNGenerator.validate_irn(irn):
            raise ValueError("Invalid IRN format")
        
        parts = irn.split('-')
        
        # Last part is date stamp, second to last is service ID
        date_stamp = parts[-1]
        service_id = parts[-2]
        # Everything else is the invoice number
        invoice_number = '-'.join(parts[:-2])
        
        # Parse date
        issue_date = datetime.strptime(date_stamp, "%Y%m%d")
        
        return {
            'invoice_number': invoice_number,
            'service_id': service_id,
            'date_stamp': date_stamp,
            'issue_date': issue_date
        }
    
    @staticmethod
    def create_custom_irn(invoice_number: str, service_id: str = None, 
                         issue_date: datetime = None) -> str:
        """Create custom IRN with specific components."""
        if service_id is None:
            service_id = IRNGenerator._generate_service_id()
        
        if issue_date is None:
            issue_date = datetime.now()
        
        date_stamp = IRNGenerator._generate_date_stamp(issue_date)
        
        irn = f"{invoice_number}-{service_id}-{date_stamp}"
        
        if not IRNGenerator.validate_irn(irn):
            raise ValueError("Generated IRN is invalid")
        
        return irn