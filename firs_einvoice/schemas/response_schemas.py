"""API response Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime, date
from decimal import Decimal
from ..models.enums import InvoiceStatus


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    
    success: bool = Field(
        ...,
        description="Request success status"
    )
    data: Optional[T] = Field(
        None,
        description="Response data"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if failed"
    )
    error_code: Optional[str] = Field(
        None,
        description="Error code for debugging"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ValidationError(BaseModel):
    """Validation error detail."""
    
    field: str = Field(
        ...,
        description="Field with error"
    )
    message: str = Field(
        ...,
        description="Error message"
    )
    code: Optional[str] = Field(
        None,
        description="Error code"
    )
    value: Optional[Any] = Field(
        None,
        description="Invalid value"
    )


class FIRSValidationResponse(BaseModel):
    """FIRS validation response model."""
    
    valid: bool = Field(
        ...,
        description="Validation status"
    )
    irn: Optional[str] = Field(
        None,
        description="Generated IRN if valid"
    )
    errors: List[ValidationError] = Field(
        default_factory=list,
        description="Validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Validation warnings"
    )
    validation_id: Optional[str] = Field(
        None,
        description="Validation transaction ID"
    )
    validated_at: Optional[datetime] = Field(
        None,
        description="Validation timestamp"
    )
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0


class InvoiceSubmissionResult(BaseModel):
    """Invoice submission result model."""
    
    success: bool = Field(
        ...,
        description="Submission status"
    )
    irn: str = Field(
        ...,
        description="Invoice Reference Number"
    )
    invoice_number: str = Field(
        ...,
        description="Original invoice number"
    )
    qr_code: Optional[str] = Field(
        None,
        description="Generated QR code data"
    )
    qr_code_url: Optional[str] = Field(
        None,
        description="QR code image URL"
    )
    submission_date: datetime = Field(
        ...,
        description="Submission timestamp"
    )
    status: InvoiceStatus = Field(
        ...,
        description="Current invoice status"
    )
    reference_number: Optional[str] = Field(
        None,
        description="FIRS reference number"
    )
    pdf_url: Optional[str] = Field(
        None,
        description="Invoice PDF URL"
    )
    xml_url: Optional[str] = Field(
        None,
        description="Invoice XML URL"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if submission failed"
    )
    error_details: List[str] = Field(
        default_factory=list,
        description="Detailed error messages"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class InvoiceStatusResponse(BaseModel):
    """Invoice status response model."""
    
    irn: str = Field(
        ...,
        description="Invoice Reference Number"
    )
    invoice_number: str = Field(
        ...,
        description="Original invoice number"
    )
    status: InvoiceStatus = Field(
        ...,
        description="Current status"
    )
    submitted_at: datetime = Field(
        ...,
        description="Submission timestamp"
    )
    last_updated: datetime = Field(
        ...,
        description="Last update timestamp"
    )
    supplier_name: str = Field(
        ...,
        description="Supplier name"
    )
    customer_name: str = Field(
        ...,
        description="Customer name"
    )
    total_amount: Decimal = Field(
        ...,
        description="Invoice total amount"
    )
    currency: str = Field(
        ...,
        description="Invoice currency"
    )
    cancellation_reason: Optional[str] = Field(
        None,
        description="Cancellation reason if cancelled"
    )
    cancelled_at: Optional[datetime] = Field(
        None,
        description="Cancellation timestamp"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: str,
        }


class BatchValidationResult(BaseModel):
    """Batch validation result model."""
    
    total: int = Field(
        ...,
        description="Total invoices processed"
    )
    valid: int = Field(
        ...,
        description="Valid invoices count"
    )
    invalid: int = Field(
        ...,
        description="Invalid invoices count"
    )
    results: List[FIRSValidationResponse] = Field(
        ...,
        description="Individual validation results"
    )
    batch_id: Optional[str] = Field(
        None,
        description="Batch processing ID"
    )
    processed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Processing timestamp"
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total == 0:
            return 0.0
        return (self.valid / self.total) * 100


class BatchSubmissionResult(BaseModel):
    """Batch submission result model."""
    
    total: int = Field(
        ...,
        description="Total invoices submitted"
    )
    successful: int = Field(
        ...,
        description="Successfully submitted count"
    )
    failed: int = Field(
        ...,
        description="Failed submission count"
    )
    results: List[InvoiceSubmissionResult] = Field(
        ...,
        description="Individual submission results"
    )
    batch_id: Optional[str] = Field(
        None,
        description="Batch processing ID"
    )
    submitted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Submission timestamp"
    )


class ResourceResponse(BaseModel):
    """Generic resource response model."""
    
    code: str = Field(
        ...,
        description="Resource code"
    )
    name: str = Field(
        ...,
        description="Resource name"
    )
    description: Optional[str] = Field(
        None,
        description="Resource description"
    )
    active: bool = Field(
        default=True,
        description="Active status"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata"
    )


class VATExemption(ResourceResponse):
    """VAT exemption resource model."""
    
    hsn_code: str = Field(
        ...,
        description="HSN code"
    )
    category: str = Field(
        ...,
        description="Product category"
    )
    exemption_reason: str = Field(
        ...,
        description="Exemption reason"
    )
    effective_date: Optional[date] = Field(
        None,
        description="Effective date"
    )
    expiry_date: Optional[date] = Field(
        None,
        description="Expiry date"
    )


class ProductCode(ResourceResponse):
    """Product code resource model."""
    
    hsn_code: str = Field(
        ...,
        description="HSN code"
    )
    category: str = Field(
        ...,
        description="Product category"
    )
    tax_rate: Decimal = Field(
        ...,
        description="Default tax rate"
    )
    unit_of_measure: str = Field(
        ...,
        description="Default unit"
    )


class ServiceCode(ResourceResponse):
    """Service code resource model."""
    
    sac_code: str = Field(
        ...,
        description="SAC code"
    )
    category: str = Field(
        ...,
        description="Service category"
    )
    tax_rate: Decimal = Field(
        ...,
        description="Default tax rate"
    )


class State(ResourceResponse):
    """State resource model."""
    
    state_code: str = Field(
        ...,
        description="State code"
    )
    region: Optional[str] = Field(
        None,
        description="Region"
    )
    capital: Optional[str] = Field(
        None,
        description="State capital"
    )


class LGA(ResourceResponse):
    """Local Government Area resource model."""
    
    lga_code: str = Field(
        ...,
        description="LGA code"
    )
    state_code: str = Field(
        ...,
        description="Parent state code"
    )
    headquarters: Optional[str] = Field(
        None,
        description="LGA headquarters"
    )


class ErrorResponse(BaseModel):
    """API error response model."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    error_code: str = Field(
        ...,
        description="Error code"
    )
    status_code: int = Field(
        ...,
        description="HTTP status code"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID for tracking"
    )