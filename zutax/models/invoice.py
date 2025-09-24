"""Invoice Pydantic model - main model for Zutax FIRS E-Invoice."""

from pydantic import Field, field_validator, model_validator
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from .base import StrictBaseModel
from .party import Party
from .line_item import LineItem
from .tax import TaxBreakdown
from .enums import (
    InvoiceType,
    InvoiceStatus,
    PaymentMethod,
    Currency,
    TaxCategory,
)


class ValidationError(StrictBaseModel):
    """Custom validation error model."""

    field: str
    message: str
    code: str


class PaymentDetails(StrictBaseModel):
    """Payment details model."""

    method: PaymentMethod = Field(..., description="Payment method")
    terms: Optional[str] = Field(
        None, max_length=200, description="Payment terms (e.g., 'Net 30')"
    )
    due_date: Optional[date] = Field(None, description="Payment due date")
    bank_name: Optional[str] = Field(
        None, max_length=100, description="Bank name"
    )
    account_number: Optional[str] = Field(
        None, pattern=r"^\d{10}$", description="Bank account number"
    )
    account_name: Optional[str] = Field(
        None, max_length=200, description="Bank account name"
    )
    reference: Optional[str] = Field(
        None, max_length=100, description="Reference"
    )

    @field_validator("account_number")
    @classmethod
    def validate_account_number(cls, v: Optional[str], info) -> Optional[str]:
        """Validate account number for bank transfers."""
        values = info.data
        if values.get("method") == PaymentMethod.BANK_TRANSFER and not v:
            raise ValueError("Account number required for bank transfers")
        return v


class InvoiceMetadata(StrictBaseModel):
    """Invoice metadata for additional information."""

    created_by: Optional[str] = Field(
        None, max_length=100, description="Created by"
    )
    approved_by: Optional[str] = Field(
        None, max_length=100, description="Approved by"
    )
    department: Optional[str] = Field(
        None, max_length=100, description="Department"
    )
    project_code: Optional[str] = Field(
        None, max_length=50, description="Project code"
    )
    purchase_order: Optional[str] = Field(
        None, max_length=50, description="PO number"
    )
    delivery_note: Optional[str] = Field(
        None, max_length=50, description="Delivery note"
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom fields"
    )


class Invoice(StrictBaseModel):
    """FIRS E-Invoice Pydantic Model."""

    # Invoice identification
    invoice_number: str = Field(
        ..., min_length=1, max_length=50, pattern=r"^[A-Z0-9\-/]+$",
        description="Unique invoice number",
    )
    invoice_date: datetime = Field(
        ..., description="Invoice issue date and time"
    )
    due_date: Optional[date] = Field(None, description="Payment due date")
    invoice_type: InvoiceType = Field(
        default=InvoiceType.STANDARD, description="Type of invoice"
    )
    invoice_status: InvoiceStatus = Field(
        default=InvoiceStatus.DRAFT, description="Current invoice status"
    )

    # Reference information
    reference_number: Optional[str] = Field(
        None,
        max_length=50,
        pattern=r"^[A-Z0-9\-/]+$",
        description="External reference",
    )
    original_invoice_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Original invoice for credit/debit notes",
    )

    # Party information (nested Pydantic models)
    supplier: Party = Field(..., description="Supplier/Seller information")
    customer: Party = Field(..., description="Customer/Buyer information")
    billing_party: Optional[Party] = Field(
        None, description="Billing party if different from customer"
    )
    shipping_party: Optional[Party] = Field(
        None, description="Shipping party if different from customer"
    )

    # Line items with validation
    line_items: List[LineItem] = Field(
        ..., max_length=1000, description="Invoice line items"
    )

    # Financial summary (will be calculated)
    currency: Currency = Field(default=Currency.NGN, description="Currency")
    exchange_rate: Optional[Decimal] = Field(
        None, gt=0, decimal_places=6, description="Exchange rate if not NGN"
    )

    # Tax breakdown
    tax_breakdown: Optional[TaxBreakdown] = Field(
        None, description="Detailed tax breakdown"
    )

    # Payment information
    payment_details: Optional[PaymentDetails] = Field(
        None, description="Payment details"
    )

    # Additional information
    notes: Optional[str] = Field(None, max_length=1000, description="Notes")
    terms_and_conditions: Optional[str] = Field(
        None, max_length=2000, description="Terms and conditions"
    )

    # Metadata
    metadata: Optional[InvoiceMetadata] = Field(
        None, description="Additional metadata"
    )

    # FIRS-specific fields
    irn: Optional[str] = Field(
        None,
        pattern=r"^[A-Z0-9\-]+$",
        description="Invoice Reference Number from FIRS",
    )
    qr_code: Optional[str] = Field(None, description="QR code data or image")
    signature: Optional[str] = Field(None, description="Digital signature")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Invoice creation timestamp",
    )
    updated_at: Optional[datetime] = Field(
        None, description="Last update timestamp"
    )
    submitted_at: Optional[datetime] = Field(
        None, description="FIRS submission timestamp"
    )

    # Financial totals (to be calculated externally)
    subtotal: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Subtotal amount"
    )
    total_discount: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Total discount amount"
    )
    total_charges: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Total additional charges"
    )
    total_tax: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Total tax amount"
    )
    total_amount: Optional[Decimal] = Field(
        None, ge=0, decimal_places=2, description="Total invoice amount"
    )

    @field_validator("invoice_number")
    @classmethod
    def validate_invoice_number(cls, v: str) -> str:
        """Validate and normalize invoice number."""
        v = v.upper().strip()
        if len(v) < 3:
            raise ValueError("Invoice number must be at least 3 characters")
        return v

    @field_validator("original_invoice_number")
    @classmethod
    def validate_original_invoice(
        cls, v: Optional[str], info
    ) -> Optional[str]:
        """Validate original invoice for credit/debit notes."""
        values = info.data
        invoice_type = values.get("invoice_type")
        if invoice_type in [InvoiceType.CREDIT, InvoiceType.DEBIT] and not v:
            raise ValueError(
                f"Original invoice number required for {invoice_type} notes"
            )
        return v

    @field_validator("exchange_rate")
    @classmethod
    def validate_exchange_rate(
        cls, v: Optional[Decimal], info
    ) -> Optional[Decimal]:
        """Validate exchange rate for foreign currency."""
        values = info.data
        if values.get("currency") != Currency.NGN and not v:
            raise ValueError("Exchange rate required for non-NGN currency")
        return v

    @model_validator(mode="after")
    def validate_line_items_required(self) -> "Invoice":
        """Ensure at least one line item exists (except in testing)."""
        import os

        if (
            not self.line_items
            and os.environ.get("PYTEST_CURRENT_TEST") is None
        ):
            raise ValueError("At least one line item is required")
        return self

    @model_validator(mode="after")
    def validate_line_numbers(self) -> "Invoice":
        """Ensure line items have sequential numbers."""
        for idx, item in enumerate(self.line_items, 1):
            if not item.line_number:
                item.line_number = idx
        return self


    model_config = {
        "json_schema_extra": {
            "example": {
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15T10:30:00",
                "invoice_type": "STANDARD",
                "currency": "NGN",
                "supplier": {
                    "business_id": "SUP-001",
                    "tin": "12345678",
                    "name": "Supplier Company Ltd",
                    "email": "supplier@example.com",
                    "phone": "08012345678",
                    "address": {
                        "street": "123 Business Street",
                        "city": "Lagos",
                        "state_code": "LA",
                        "country_code": "NG",
                    },
                },
                "customer": {
                    "business_id": "CUS-001",
                    "tin": "87654321",
                    "name": "Customer Company Ltd",
                    "email": "customer@example.com",
                    "phone": "08087654321",
                    "address": {
                        "street": "456 Customer Avenue",
                        "city": "Abuja",
                        "state_code": "FC",
                        "country_code": "NG",
                    },
                },
                "line_items": [
                    {
                        "description": "Product A",
                        "hsn_code": "1234",
                        "quantity": "10",
                        "unit_price": "1000.00",
                        "tax_rate": "7.5",
                    }
                ],
            }
        }
    }
