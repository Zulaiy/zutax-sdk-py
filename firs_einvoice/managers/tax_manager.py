"""Tax calculation and management utilities."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from .hsn_manager import HSNManager
from ..config.constants import DEFAULT_CONFIG, TAX_CATEGORIES
from ..models.tax import Tax


class TaxCalculation(BaseModel):
    """Tax calculation result model."""
    category: str
    rate: float
    base_amount: Decimal
    tax_amount: Decimal
    exemption_reason: Optional[str] = None


class TaxBreakdown(BaseModel):
    """Comprehensive tax breakdown model."""
    vat: Decimal
    excise: Decimal
    customs: Decimal
    other: Decimal
    total: Decimal
    details: List[TaxCalculation]


class TaxManager:
    """Tax calculation and management utilities."""
    
    VAT_RATE = DEFAULT_CONFIG['DEFAULT_TAX_RATE']
    EXCISE_RATES = {
        'TOBACCO': 20,
        'ALCOHOL': 15,
        'LUXURY': 10
    }
    
    @classmethod
    def calculate_line_tax(cls, amount: float, hsn_code: str = None, 
                          custom_rate: float = None) -> TaxCalculation:
        """Calculate tax for a line item."""
        base_amount = Decimal(str(amount))
        
        # Check for HSN-based exemption
        if hsn_code and HSNManager.is_exempt(hsn_code):
            calculation = TaxCalculation(
                category=TAX_CATEGORIES['STANDARD_VAT'],
                rate=0,
                base_amount=base_amount,
                tax_amount=Decimal('0')
            )
            reason = HSNManager.get_exemption_reason(hsn_code)
            if reason:
                calculation.exemption_reason = reason
            return calculation
        
        # Use custom rate or HSN rate or default rate
        if custom_rate is not None:
            rate = custom_rate
        elif hsn_code:
            rate = HSNManager.get_tax_rate(hsn_code)
        else:
            rate = cls.VAT_RATE
        
        tax_amount = (base_amount * Decimal(str(rate)) / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return TaxCalculation(
            category=TAX_CATEGORIES['STANDARD_VAT'],
            rate=rate,
            base_amount=base_amount,
            tax_amount=tax_amount
        )
    
    @classmethod
    def calculate_multiple_taxes(cls, amount: float, 
                                taxes: List[Dict[str, Any]]) -> TaxBreakdown:
        """Calculate multiple taxes for an amount."""
        base_amount = Decimal(str(amount))
        breakdown = TaxBreakdown(
            vat=Decimal('0'),
            excise=Decimal('0'),
            customs=Decimal('0'),
            other=Decimal('0'),
            total=Decimal('0'),
            details=[]
        )
        
        for tax in taxes:
            tax_amount = (base_amount * Decimal(str(tax['rate'])) / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            calculation = TaxCalculation(
                category=tax['category'],
                rate=tax['rate'],
                base_amount=base_amount,
                tax_amount=tax_amount
            )
            
            breakdown.details.append(calculation)
            
            # Categorize tax
            category = tax['category']
            if category in [TAX_CATEGORIES['STANDARD_VAT'], TAX_CATEGORIES['REDUCED_VAT'], 
                           TAX_CATEGORIES['ZERO_VAT']]:
                breakdown.vat += tax_amount
            elif category in [TAX_CATEGORIES['ALCOHOL_EXCISE_TAX'], TAX_CATEGORIES['TOBACCO_EXCISE_TAX'],
                             TAX_CATEGORIES['FUEL_EXCISE_TAX']]:
                breakdown.excise += tax_amount
            elif category in [TAX_CATEGORIES['IMPORT_DUTY'], TAX_CATEGORIES['EXPORT_DUTY']]:
                breakdown.customs += tax_amount
            else:
                breakdown.other += tax_amount
            
            breakdown.total += tax_amount
        
        return breakdown
    
    @classmethod
    def calculate_cascading_tax(cls, amount: float, 
                               taxes: List[Dict[str, Any]]) -> TaxBreakdown:
        """Calculate tax with cascading effect."""
        current_amount = Decimal(str(amount))
        breakdown = TaxBreakdown(
            vat=Decimal('0'),
            excise=Decimal('0'),
            customs=Decimal('0'),
            other=Decimal('0'),
            total=Decimal('0'),
            details=[]
        )
        
        for tax in taxes:
            tax_amount = (current_amount * Decimal(str(tax['rate'])) / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            calculation = TaxCalculation(
                category=tax['category'],
                rate=tax['rate'],
                base_amount=current_amount,
                tax_amount=tax_amount
            )
            
            breakdown.details.append(calculation)
            current_amount += tax_amount  # Add tax to base for next calculation
            
            # Categorize tax
            category = tax['category']
            if category in [TAX_CATEGORIES['STANDARD_VAT'], TAX_CATEGORIES['REDUCED_VAT'], 
                           TAX_CATEGORIES['ZERO_VAT']]:
                breakdown.vat += tax_amount
            elif category in [TAX_CATEGORIES['ALCOHOL_EXCISE_TAX'], TAX_CATEGORIES['TOBACCO_EXCISE_TAX'],
                             TAX_CATEGORIES['FUEL_EXCISE_TAX']]:
                breakdown.excise += tax_amount
            elif category in [TAX_CATEGORIES['IMPORT_DUTY'], TAX_CATEGORIES['EXPORT_DUTY']]:
                breakdown.customs += tax_amount
            else:
                breakdown.other += tax_amount
            
            breakdown.total += tax_amount
        
        return breakdown
    
    @classmethod
    def calculate_reverse_tax(cls, total_amount: float, 
                             tax_rate: float) -> Dict[str, Decimal]:
        """Calculate reverse tax (tax inclusive price)."""
        total = Decimal(str(total_amount))
        divisor = (Decimal('100') + Decimal(str(tax_rate))) / Decimal('100')
        base_amount = (total / divisor).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tax_amount = total - base_amount
        
        return {
            'base_amount': base_amount,
            'tax_amount': tax_amount
        }
    
    @classmethod
    def validate_tax_calculation(cls, base_amount: float, tax_amount: float, 
                                rate: float) -> bool:
        """Validate tax calculations."""
        base = Decimal(str(base_amount))
        tax = Decimal(str(tax_amount))
        expected_tax = (base * Decimal(str(rate)) / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Allow for small rounding differences (0.01)
        difference = abs(tax - expected_tax)
        return difference <= Decimal('0.01')
    
    @classmethod
    def tax_to_calculation(cls, tax: Tax, base_amount: Decimal) -> TaxCalculation:
        """Convert Tax object to TaxCalculation."""
        calculation = TaxCalculation(
            category=tax.category,
            rate=tax.rate,
            base_amount=base_amount,
            tax_amount=tax.amount
        )
        
        if tax.exemption_reason:
            calculation.exemption_reason = tax.exemption_reason
        
        return calculation
    
    @classmethod
    def get_excise_rate(cls, category: str) -> float:
        """Get excise rate for a category."""
        return cls.EXCISE_RATES.get(category.upper(), 0)
    
    @classmethod
    def calculate_withholding_tax(cls, amount: float, rate: float = 10) -> Decimal:
        """Calculate withholding tax."""
        base_amount = Decimal(str(amount))
        return (base_amount * Decimal(str(rate)) / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    @classmethod
    def format_tax_amount(cls, amount: float, currency: str = 'NGN') -> str:
        """Format tax amount for display."""
        value = Decimal(str(amount))
        return f"{currency} {value.quantize(Decimal('0.01'))}"
    
    @classmethod
    def get_tax_summary(cls, calculations: List[TaxCalculation]) -> Dict[str, Any]:
        """Get tax summary from multiple calculations."""
        total_base = sum((calc.base_amount for calc in calculations), Decimal('0'))
        total_tax = sum((calc.tax_amount for calc in calculations), Decimal('0'))
        
        categories = {}
        for calc in calculations:
            if calc.category not in categories:
                categories[calc.category] = Decimal('0')
            categories[calc.category] += calc.tax_amount
        
        effective_rate = 0
        if total_base > 0:
            effective_rate = float((total_tax / total_base * Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            ))
        
        return {
            'total_base': total_base,
            'total_tax': total_tax,
            'effective_rate': effective_rate,
            'categories': categories
        }
    
    @classmethod
    def apply_tax_holiday(cls, amount: float, standard_rate: float, 
                         holiday_rate: float, is_holiday_applicable: bool) -> TaxCalculation:
        """Apply tax holidays or special rates."""
        base_amount = Decimal(str(amount))
        rate = holiday_rate if is_holiday_applicable else standard_rate
        tax_amount = (base_amount * Decimal(str(rate)) / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        calculation = TaxCalculation(
            category=TAX_CATEGORIES['STANDARD_VAT'],
            rate=rate,
            base_amount=base_amount,
            tax_amount=tax_amount
        )
        
        if is_holiday_applicable:
            calculation.exemption_reason = 'Tax holiday applied'
        
        return calculation