"""Response schemas (Zutax)."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class FIRSValidationResponse(BaseModel):
    """Schema for FIRS validation response."""

    valid: bool = Field(...)
    errors: Optional[list] = Field(default=None)
    warnings: Optional[list] = Field(default=None)


class InvoiceSubmissionResult(BaseModel):
    """Schema for invoice submission response."""

    success: bool = Field(...)
    irn: Optional[str] = None
    submission_date: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
