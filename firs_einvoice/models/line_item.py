"""Line item Pydantic models for invoice items."""

from pydantic import Field, field_validator, computed_field
from decimal import Decimal
from typing import Optional, List
from .base import FIRSBaseModel, StrictBaseModel
from .enums import UnitOfMeasure, TaxCategory


class Discount(FIRSBaseModel):
    """Discount model for line items."""
    
    amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Discount amount"
    )
    percent: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        decimal_places=2,
        description="Discount percentage"
    )
    description: Optional[str] = Field(
        None,
        max_length=100,
        description="Discount description"
    )
    
    @field_validator('amount', 'percent')
    @classmethod
    def validate_discount(cls, v, info):
        """Ensure either amount or percent is provided, not both."""
        values = info.data
        if values.get('amount') and values.get('percent'):
            raise ValueError('Cannot specify both discount amount and percentage')
        return v


class Charge(FIRSBaseModel):
    """Additional charge model for line items."""
    
    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Charge amount"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Charge description"
    )
    tax_category: Optional[TaxCategory] = Field(
        None,
        description="Tax category for the charge"
    )


class LineItem(StrictBaseModel):
    """Line item Pydantic model for invoice items."""
    
    # Item identification
    item_id: Optional[str] = Field(
        None,
        pattern=r'^[A-Z0-9\-]+$',
        max_length=50,
        description="Unique item identifier"
    )
    line_number: Optional[int] = Field(
        None,
        ge=1,
        description="Line item sequence number"
    )
    
    # Product/Service details
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Item description"
    )
    hsn_code: str = Field(
        ...,
        pattern=r'^\d{4,8}$',
        description="HSN/SAC code (4-8 digits)"
    )
    product_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Internal product code"
    )
    barcode: Optional[str] = Field(
        None,
        pattern=r'^[0-9]+$',
        max_length=20,
        description="Product barcode (EAN/UPC)"
    )
    batch_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Batch or lot number"
    )
    serial_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Serial number"
    )
    
    # Quantity and pricing
    quantity: Decimal = Field(
        ...,
        gt=0,
        decimal_places=3,
        description="Quantity"
    )
    unit_of_measure: UnitOfMeasure = Field(
        default=UnitOfMeasure.UNIT,
        description="Unit of measurement"
    )
    unit_price: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Unit price before tax"
    )
    
    # Discounts and charges
    discount: Optional[Discount] = Field(
        None,
        description="Line item discount"
    )
    charges: Optional[List[Charge]] = Field(
        None,
        max_length=10,
        description="Additional charges"
    )
    
    # Tax information
    tax_category: TaxCategory = Field(
        default=TaxCategory.VAT,
        description="Tax category"
    )
    tax_rate: Decimal = Field(
        default=Decimal("7.5"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Tax rate percentage"
    )
    tax_exempt: bool = Field(
        default=False,
        description="Tax exemption status"
    )
    tax_exempt_reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Tax exemption reason"
    )
    
    # Convenience fields for compatibility
    discount_percent: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        decimal_places=2,
        description="Discount percentage (convenience field)"
    )
    tax_exemption_reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Tax exemption reason (alias for tax_exempt_reason)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Line item notes or comments"
    )
    
    # Calculated fields (using Pydantic computed fields)
    @computed_field
    @property
    def base_amount(self) -> Decimal:
        """Calculate base amount (quantity * unit_price)."""
        return self.quantity * self.unit_price
    
    @computed_field
    @property
    def discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        # Check convenience field first
        if self.discount_percent:
            return (self.base_amount * self.discount_percent) / Decimal("100")
        
        if not self.discount:
            return Decimal("0")
        
        if self.discount.amount:
            return self.discount.amount
        elif self.discount.percent:
            return (self.base_amount * self.discount.percent) / Decimal("100")
        else:
            return Decimal("0")
    
    @computed_field
    @property
    def charge_amount(self) -> Decimal:
        """Calculate total charges."""
        if not self.charges:
            return Decimal("0")
        return sum(charge.amount for charge in self.charges)
    
    @computed_field
    @property
    def taxable_amount(self) -> Decimal:
        """Calculate taxable amount after discounts and charges."""
        return self.base_amount - self.discount_amount + self.charge_amount
    
    @computed_field
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        if self.tax_exempt:
            return Decimal("0")
        return (self.taxable_amount * self.tax_rate) / Decimal("100")
    
    @computed_field
    @property
    def line_total(self) -> Decimal:
        """Calculate line total including tax."""
        return self.taxable_amount + self.tax_amount
    
    @field_validator('hsn_code')
    @classmethod
    def validate_hsn_code(cls, v: str) -> str:
        """Validate HSN/SAC code format."""
        if not v.isdigit():
            raise ValueError('HSN code must contain only digits')
        if len(v) < 4 or len(v) > 8:
            raise ValueError('HSN code must be between 4 and 8 digits')
        return v
    
    @field_validator('tax_exempt_reason')
    @classmethod
    def validate_tax_exempt_reason(cls, v: Optional[str], info) -> Optional[str]:
        """Validate tax exemption reason is provided when exempt."""
        values = info.data
        if values.get('tax_exempt') and not v:
            raise ValueError('Tax exemption reason required when tax exempt')
        return v
    
    @field_validator('tax_exemption_reason')
    @classmethod
    def validate_tax_exemption_reason(cls, v: Optional[str], info) -> Optional[str]:
        """Set tax_exempt=True when tax_exemption_reason is provided."""
        if v:
            # If tax_exemption_reason is provided, automatically set tax_exempt
            info.data['tax_exempt'] = True
            info.data['tax_exempt_reason'] = v
        return v
    
    @field_validator('quantity', 'unit_price', 'tax_rate', mode='before')
    @classmethod
    def coerce_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "item_id": "ITEM-001",
                "line_number": 1,
                "description": "Office Laptop Computer",
                "hsn_code": "8471",
                "product_code": "LAP-001",
                "quantity": "2",
                "unit_of_measure": "PCE",
                "unit_price": "150000.00",
                "discount": {
                    "percent": "10",
                    "description": "Bulk discount"
                },
                "tax_category": "VAT",
                "tax_rate": "7.5",
                "tax_exempt": False
            }
        }
    }