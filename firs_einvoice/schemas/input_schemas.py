"""Input validation schemas with relaxed validation for user input."""

from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from ..models.enums import (
    InvoiceType,
    PaymentMethod,
    Currency,
    StateCode,
    UnitOfMeasure,
    TaxCategory,
)


class AddressInput(BaseModel):
    """Simplified address input schema."""
    
    street: str = Field(..., min_length=1)
    street2: Optional[str] = None
    city: str = Field(..., min_length=1)
    state_code: Union[StateCode, str] = Field(...)
    lga_code: Optional[str] = None
    postal_code: Optional[str] = None
    country_code: str = Field(default="NG")
    
    @field_validator('state_code', mode='before')
    @classmethod
    def validate_state_code(cls, v):
        """Convert string to StateCode enum."""
        if isinstance(v, str):
            v = v.upper()
            try:
                return StateCode(v)
            except ValueError:
                # Allow any string for flexibility
                return v
        return v


class PartyInput(BaseModel):
    """Simplified party input schema."""
    
    business_id: Optional[str] = None
    tin: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1)
    trade_name: Optional[str] = None
    email: str = Field(...)
    phone: str = Field(...)
    address: AddressInput
    vat_registered: bool = Field(default=False)
    vat_number: Optional[str] = None
    
    @field_validator('tin', mode='before')
    @classmethod
    def clean_tin(cls, v):
        """Clean TIN input."""
        if isinstance(v, str):
            return v.strip().replace("-", "").replace(" ", "")
        return v
    
    @field_validator('phone', mode='before')
    @classmethod
    def clean_phone(cls, v):
        """Clean phone input."""
        if isinstance(v, str):
            return v.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        return v


class LineItemInput(BaseModel):
    """Simplified line item input schema."""
    
    description: str = Field(..., min_length=1)
    hsn_code: str = Field(...)
    product_code: Optional[str] = None
    quantity: Union[Decimal, float, int, str] = Field(..., gt=0)
    unit_of_measure: Optional[Union[UnitOfMeasure, str]] = Field(default="UNIT")
    unit_price: Union[Decimal, float, int, str] = Field(..., ge=0)
    discount_percent: Optional[Union[Decimal, float, int, str]] = Field(default=0)
    discount_amount: Optional[Union[Decimal, float, int, str]] = Field(default=None)
    tax_category: Optional[Union[TaxCategory, str]] = Field(default="VAT")
    tax_rate: Optional[Union[Decimal, float, int, str]] = Field(default=7.5)
    tax_exempt: bool = Field(default=False)
    tax_exempt_reason: Optional[str] = None
    
    @field_validator('quantity', 'unit_price', 'discount_percent', 'discount_amount', 'tax_rate', mode='before')
    @classmethod
    def coerce_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if v is None:
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @field_validator('hsn_code', mode='before')
    @classmethod
    def clean_hsn_code(cls, v):
        """Clean HSN code input."""
        if isinstance(v, str):
            return v.strip().replace("-", "").replace(" ", "")
        return v
    
    @model_validator(mode='after')
    def validate_discount(self):
        """Ensure only one type of discount is specified."""
        if self.discount_percent and self.discount_amount:
            raise ValueError("Cannot specify both discount_percent and discount_amount")
        return self


class PaymentDetailsInput(BaseModel):
    """Simplified payment details input."""
    
    method: Union[PaymentMethod, str] = Field(...)
    terms: Optional[str] = None
    due_date: Optional[Union[date, str]] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    reference: Optional[str] = None
    
    @field_validator('due_date', mode='before')
    @classmethod
    def parse_due_date(cls, v):
        """Parse due date from string."""
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.strptime(v, "%d/%m/%Y").date()
                except ValueError:
                    raise ValueError("Invalid date format. Use YYYY-MM-DD or DD/MM/YYYY")
        return v


class InvoiceInput(BaseModel):
    """Simplified invoice input schema for easy data entry."""
    
    # Invoice identification
    invoice_number: Optional[str] = None
    invoice_date: Optional[Union[datetime, str]] = None
    invoice_type: Union[InvoiceType, str] = Field(default="STANDARD")
    
    # Reference information
    reference_number: Optional[str] = None
    original_invoice_number: Optional[str] = None
    
    # Party information (can use IDs or full objects)
    supplier: Optional[Union[str, PartyInput]] = None
    supplier_id: Optional[str] = None
    customer: Optional[Union[str, PartyInput]] = None
    customer_id: Optional[str] = None
    
    # Line items
    items: List[LineItemInput] = Field(..., min_length=1)
    
    # Financial
    currency: Union[Currency, str] = Field(default="NGN")
    exchange_rate: Optional[Union[Decimal, float, str]] = None
    
    # Payment
    payment_details: Optional[PaymentDetailsInput] = None
    
    # Additional information
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @field_validator('invoice_date', mode='before')
    @classmethod
    def parse_invoice_date(cls, v):
        """Parse invoice date from string."""
        if v is None:
            return datetime.now()
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(v, "%d/%m/%Y")
                except ValueError:
                    try:
                        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        raise ValueError("Invalid date format")
        return v
    
    @field_validator('exchange_rate', mode='before')
    @classmethod
    def coerce_exchange_rate(cls, v):
        """Convert exchange rate to Decimal."""
        if v is None:
            return v
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    @model_validator(mode='after')
    def validate_parties(self):
        """Ensure supplier and customer are provided."""
        if not self.supplier and not self.supplier_id:
            raise ValueError("Either supplier or supplier_id must be provided")
        if not self.customer and not self.customer_id:
            raise ValueError("Either customer or customer_id must be provided")
        return self
    
    @model_validator(mode='after')
    def generate_invoice_number(self):
        """Generate invoice number if not provided."""
        if not self.invoice_number:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            prefix = "INV"
            if self.invoice_type == InvoiceType.CREDIT:
                prefix = "CRN"
            elif self.invoice_type == InvoiceType.DEBIT:
                prefix = "DBN"
            self.invoice_number = f"{prefix}-{timestamp}"
        return self
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


def validate_invoice_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate invoice input data."""
    try:
        validated_input = InvoiceInput(**data)
        return {
            'success': True,
            'data': validated_input.model_dump(),
            'errors': []
        }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'errors': [{'message': str(e), 'path': []}]
        }


class BulkInvoiceInput(BaseModel):
    """Input schema for bulk invoice operations."""
    
    invoices: List[InvoiceInput] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of invoices to process"
    )
    validate_only: bool = Field(
        default=False,
        description="Only validate without submission"
    )
    stop_on_error: bool = Field(
        default=False,
        description="Stop processing on first error"
    )
    
    @field_validator('invoices')
    @classmethod
    def validate_invoice_count(cls, v):
        """Validate invoice count for bulk operations."""
        if len(v) > 100:
            raise ValueError("Maximum 100 invoices allowed in bulk operation")
        return v