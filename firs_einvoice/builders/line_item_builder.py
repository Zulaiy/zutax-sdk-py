"""Line item builder with fluent interface."""

from typing import Optional, List, Union
from decimal import Decimal
from ..models import LineItem, Discount, Charge, UnitOfMeasure, TaxCategory


class LineItemBuilder:
    """Fluent builder for creating LineItem objects with Pydantic validation."""
    
    def __init__(self):
        """Initialize line item builder."""
        self._item_data = {}
        self._charges: List[Charge] = []
        
        # Set defaults
        self._item_data["unit_of_measure"] = UnitOfMeasure.UNIT
        self._item_data["tax_category"] = TaxCategory.VAT
        self._item_data["tax_rate"] = Decimal("7.5")
        self._item_data["tax_exempt"] = False
    
    def with_item_id(self, item_id: str) -> 'LineItemBuilder':
        """Set item ID."""
        self._item_data["item_id"] = item_id
        return self
    
    def with_line_number(self, line_number: int) -> 'LineItemBuilder':
        """Set line number."""
        self._item_data["line_number"] = line_number
        return self
    
    def with_description(self, description: str) -> 'LineItemBuilder':
        """Set item description."""
        self._item_data["description"] = description
        return self
    
    def with_hsn_code(self, hsn_code: str) -> 'LineItemBuilder':
        """
        Set HSN/SAC code.
        
        Args:
            hsn_code: HSN or SAC code (4-8 digits)
        """
        self._item_data["hsn_code"] = hsn_code
        
        # Auto-detect VAT exemption based on HSN code
        from ..schemas.validators import is_vat_exempt
        if is_vat_exempt(hsn_code):
            self._item_data["tax_exempt"] = True
            self._item_data["tax_exempt_reason"] = "HSN code is VAT exempt"
        
        return self
    
    def with_product_code(self, product_code: str) -> 'LineItemBuilder':
        """Set internal product code."""
        self._item_data["product_code"] = product_code
        return self
    
    def with_barcode(self, barcode: str) -> 'LineItemBuilder':
        """Set product barcode."""
        self._item_data["barcode"] = barcode
        return self
    
    def with_batch_number(self, batch_number: str) -> 'LineItemBuilder':
        """Set batch number."""
        self._item_data["batch_number"] = batch_number
        return self
    
    def with_serial_number(self, serial_number: str) -> 'LineItemBuilder':
        """Set serial number."""
        self._item_data["serial_number"] = serial_number
        return self
    
    def with_quantity(
        self,
        quantity: Union[Decimal, float, int],
        unit_of_measure: Optional[Union[UnitOfMeasure, str]] = None
    ) -> 'LineItemBuilder':
        """
        Set quantity and unit of measure.
        
        Args:
            quantity: Quantity value
            unit_of_measure: Optional unit of measure
        """
        self._item_data["quantity"] = Decimal(str(quantity))
        
        if unit_of_measure:
            if isinstance(unit_of_measure, str):
                unit_of_measure = UnitOfMeasure(unit_of_measure.upper())
            self._item_data["unit_of_measure"] = unit_of_measure
        
        return self
    
    def with_unit_price(self, unit_price: Union[Decimal, float]) -> 'LineItemBuilder':
        """Set unit price before tax."""
        self._item_data["unit_price"] = Decimal(str(unit_price))
        return self
    
    def with_discount_percent(self, percent: Union[Decimal, float]) -> 'LineItemBuilder':
        """
        Set discount as percentage.
        
        Args:
            percent: Discount percentage (0-100)
        """
        percent_decimal = Decimal(str(percent))
        self._item_data["discount_percent"] = percent_decimal
        
        # Also set the discount object for compatibility
        discount = Discount(
            percent=percent_decimal,
            description=f"{percent}% discount"
        )
        self._item_data["discount"] = discount
        return self
    
    def with_discount_amount(
        self,
        amount: Union[Decimal, float],
        description: Optional[str] = None
    ) -> 'LineItemBuilder':
        """
        Set discount as fixed amount.
        
        Args:
            amount: Discount amount
            description: Optional discount description
        """
        discount = Discount(
            amount=Decimal(str(amount)),
            description=description or "Fixed discount"
        )
        self._item_data["discount"] = discount
        return self
    
    def with_discount(self, discount: Discount) -> 'LineItemBuilder':
        """Set discount object directly."""
        self._item_data["discount"] = discount
        return self
    
    def add_charge(
        self,
        amount: Union[Decimal, float],
        description: str,
        tax_category: Optional[Union[TaxCategory, str]] = None
    ) -> 'LineItemBuilder':
        """
        Add an additional charge.
        
        Args:
            amount: Charge amount
            description: Charge description
            tax_category: Optional tax category for the charge
        """
        if tax_category and isinstance(tax_category, str):
            tax_category = TaxCategory(tax_category.upper())
        
        charge = Charge(
            amount=Decimal(str(amount)),
            description=description,
            tax_category=tax_category
        )
        self._charges.append(charge)
        return self
    
    def with_charge(
        self,
        amount: Union[Decimal, float],
        description: str,
        tax_category: Optional[Union[TaxCategory, str]] = None
    ) -> 'LineItemBuilder':
        """
        Add an additional charge (alias for add_charge).
        
        Args:
            amount: Charge amount
            description: Charge description
            tax_category: Optional tax category for the charge
        """
        return self.add_charge(amount, description, tax_category)
    
    def with_tax(
        self,
        tax_rate: Union[Decimal, float],
        tax_category: Optional[Union[TaxCategory, str]] = None
    ) -> 'LineItemBuilder':
        """
        Set tax information.
        
        Args:
            tax_rate: Tax rate percentage
            tax_category: Optional tax category
        """
        self._item_data["tax_rate"] = Decimal(str(tax_rate))
        
        if tax_category:
            if isinstance(tax_category, str):
                tax_category = TaxCategory(tax_category.upper())
            self._item_data["tax_category"] = tax_category
        
        return self
    
    def with_tax_exemption(self, reason: str) -> 'LineItemBuilder':
        """
        Mark item as tax exempt.
        
        Args:
            reason: Tax exemption reason
        """
        self._item_data["tax_exempt"] = True
        self._item_data["tax_exempt_reason"] = reason
        self._item_data["tax_exemption_reason"] = reason  # alias
        self._item_data["tax_rate"] = Decimal("0")
        return self
    
    def with_notes(self, notes: str) -> 'LineItemBuilder':
        """Set line item notes."""
        self._item_data["notes"] = notes
        return self
    
    def reset(self) -> 'LineItemBuilder':
        """Reset builder to initial state."""
        self._item_data = {
            "unit_of_measure": UnitOfMeasure.UNIT,
            "tax_category": TaxCategory.VAT,
            "tax_rate": Decimal("7.5"),
            "tax_exempt": False,
        }
        self._charges = []
        return self
    
    def validate(self) -> bool:
        """
        Validate if line item can be built.
        
        Returns:
            True if valid, raises ValueError if not
        """
        if not self._item_data.get("description"):
            raise ValueError("Item description is required")
        
        if not self._item_data.get("hsn_code"):
            raise ValueError("HSN/SAC code is required")
        
        if not self._item_data.get("quantity"):
            raise ValueError("Quantity is required")
        
        if self._item_data.get("quantity", 0) <= 0:
            raise ValueError("Quantity must be greater than zero")
        
        if "unit_price" not in self._item_data:
            raise ValueError("Unit price is required")
        
        if self._item_data.get("unit_price", 0) < 0:
            raise ValueError("Unit price cannot be negative")
        
        if self._item_data.get("tax_exempt") and not self._item_data.get("tax_exempt_reason"):
            raise ValueError("Tax exemption reason required when tax exempt")
        
        return True
    
    def build(self) -> LineItem:
        """
        Build and return the LineItem object.
        
        Returns:
            Validated LineItem object
            
        Raises:
            ValueError: If required fields are missing
            ValidationError: If Pydantic validation fails
        """
        self.validate()
        
        # Add charges if any
        if self._charges:
            self._item_data["charges"] = self._charges
        
        # Create and return LineItem with Pydantic validation
        return LineItem(**self._item_data)
    
    def build_dict(self) -> dict:
        """
        Build and return line item as dictionary.
        
        Returns:
            LineItem data as dictionary
        """
        item = self.build()
        return item.model_dump(exclude_none=True, by_alias=True)
    
    def build_json(self) -> str:
        """
        Build and return line item as JSON string.
        
        Returns:
            LineItem data as JSON string
        """
        item = self.build()
        return item.model_dump_json(exclude_none=True, by_alias=True)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LineItemBuilder':
        """
        Create builder from dictionary data.
        
        Args:
            data: LineItem data as dictionary
            
        Returns:
            LineItemBuilder instance with data
        """
        builder = cls()
        
        # Set basic fields
        for field in ["item_id", "line_number", "description", "hsn_code",
                     "product_code", "barcode", "quantity", "unit_price"]:
            if field in data:
                builder._item_data[field] = data[field]
        
        # Set enums
        if "unit_of_measure" in data:
            builder._item_data["unit_of_measure"] = UnitOfMeasure(data["unit_of_measure"])
        
        if "tax_category" in data:
            builder._item_data["tax_category"] = TaxCategory(data["tax_category"])
        
        # Set tax fields
        for field in ["tax_rate", "tax_exempt", "tax_exempt_reason"]:
            if field in data:
                builder._item_data[field] = data[field]
        
        # Set discount
        if "discount" in data:
            builder._item_data["discount"] = Discount(**data["discount"])
        
        # Set charges
        if "charges" in data:
            builder._charges = [Charge(**charge) for charge in data["charges"]]
        
        return builder