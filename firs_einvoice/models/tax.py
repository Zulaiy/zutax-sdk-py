"""Tax-related Pydantic models."""

from pydantic import Field, computed_field
from decimal import Decimal
from typing import Optional, List, Dict
from .base import FIRSBaseModel
from .enums import TaxCategory


class Tax(FIRSBaseModel):
    """Simple tax model for line items."""
    
    category: TaxCategory = Field(
        default=TaxCategory.VAT,
        description="Tax category"
    )
    rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        decimal_places=2,
        description="Tax rate percentage"
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Tax amount"
    )
    exemption_reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Tax exemption reason if applicable"
    )


class TaxDetail(FIRSBaseModel):
    """Individual tax detail model."""
    
    category: TaxCategory = Field(
        ...,
        description="Tax category"
    )
    rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        decimal_places=2,
        description="Tax rate percentage"
    )
    taxable_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Amount subject to tax"
    )
    tax_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Calculated tax amount"
    )
    exempt_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Tax exempt amount"
    )
    description: Optional[str] = Field(
        None,
        max_length=200,
        description="Tax description or notes"
    )
    
    @computed_field
    @property
    def effective_rate(self) -> Decimal:
        """Calculate effective tax rate."""
        if self.taxable_amount == 0:
            return Decimal("0")
        return (self.tax_amount / self.taxable_amount) * Decimal("100")


class TaxBreakdown(FIRSBaseModel):
    """Complete tax breakdown for an invoice."""
    
    subtotal: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Subtotal before tax"
    )
    total_discount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Total discount amount"
    )
    total_charges: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Total additional charges"
    )
    taxable_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total taxable amount"
    )
    tax_details: List[TaxDetail] = Field(
        default_factory=list,
        description="Breakdown by tax category"
    )
    
    @computed_field
    @property
    def total_tax(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(detail.tax_amount for detail in self.tax_details)
    
    @computed_field
    @property
    def total_exempt(self) -> Decimal:
        """Calculate total exempt amount."""
        return sum(
            detail.exempt_amount or Decimal("0")
            for detail in self.tax_details
        )
    
    @computed_field
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount including tax."""
        return self.taxable_amount + self.total_tax
    
    @computed_field
    @property
    def tax_summary(self) -> Dict[str, Decimal]:
        """Generate tax summary by category."""
        summary = {}
        for detail in self.tax_details:
            category = detail.category if isinstance(detail.category, str) else detail.category.value
            if category not in summary:
                summary[category] = Decimal("0")
            summary[category] += detail.tax_amount
        return summary


class TaxCalculation(FIRSBaseModel):
    """Tax calculation result model."""
    
    base_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Base amount before tax"
    )
    discount_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Discount amount"
    )
    charge_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Additional charge amount"
    )
    taxable_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Amount subject to tax"
    )
    tax_rate: Decimal = Field(
        ...,
        ge=0,
        le=100,
        decimal_places=2,
        description="Applied tax rate"
    )
    tax_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Calculated tax amount"
    )
    total_amount: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount including tax"
    )
    
    # Tax breakdown by category
    vat_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="VAT amount"
    )
    excise_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Excise duty amount"
    )
    customs_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Customs duty amount"
    )
    withholding_amount: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Withholding tax amount"
    )
    
    # Exemption details
    is_exempt: bool = Field(
        default=False,
        description="Tax exemption status"
    )
    exemption_reason: Optional[str] = Field(
        None,
        max_length=200,
        description="Tax exemption reason"
    )
    exemption_certificate: Optional[str] = Field(
        None,
        max_length=50,
        description="Tax exemption certificate number"
    )
    
    @computed_field
    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after discounts and charges."""
        return self.base_amount - self.discount_amount + self.charge_amount
    
    @computed_field
    @property
    def effective_tax_rate(self) -> Decimal:
        """Calculate effective tax rate."""
        if self.taxable_amount == 0:
            return Decimal("0")
        return (self.tax_amount / self.taxable_amount) * Decimal("100")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "base_amount": "100000.00",
                "discount_amount": "5000.00",
                "charge_amount": "2000.00",
                "taxable_amount": "97000.00",
                "tax_rate": "7.5",
                "tax_amount": "7275.00",
                "total_amount": "104275.00",
                "vat_amount": "7275.00",
                "is_exempt": False
            }
        }
    }