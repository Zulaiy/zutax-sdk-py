"""HSN (Harmonized System of Nomenclature) code management (Zutax)."""

import re
from typing import Dict, List, Optional, Set
from pydantic import BaseModel

from ..config.constants import VAT_EXEMPTION_REASONS


class HSNCode(BaseModel):
    """HSN code model."""

    code: str
    description: str
    category: str
    tax_rate: float
    is_exempt: bool
    exemption_reason: Optional[str] = None


class HSNManager:
    """HSN code manager for tax classification and exemption handling."""

    _hsn_database: Dict[str, HSNCode] = {}
    _exempt_categories: Set[str] = {
        "MEDICAL",
        "FOOD_BASIC",
        "INFANT",
        "EDUCATION",
        "AGRICULTURE",
    }

    @classmethod
    def initialize(cls) -> None:
        """Initialize HSN database with common codes."""
        if cls._hsn_database:
            return  # Already initialized

        # Medical supplies
        cls._add_hsn_code(
            "3004",
            "Medicaments",
            "MEDICAL",
            0,
            True,
            VAT_EXEMPTION_REASONS["MEDICAL"],
        )
        cls._add_hsn_code(
            "3005",
            "Wadding, gauze, bandages",
            "MEDICAL",
            0,
            True,
            VAT_EXEMPTION_REASONS["MEDICAL"],
        )
        cls._add_hsn_code(
            "3006",
            "Pharmaceutical preparations",
            "MEDICAL",
            0,
            True,
            VAT_EXEMPTION_REASONS["MEDICAL"],
        )

        # Basic food items
        cls._add_hsn_code(
            "1001",
            "Wheat and meslin",
            "FOOD_BASIC",
            0,
            True,
            VAT_EXEMPTION_REASONS["FOOD"],
        )
        cls._add_hsn_code(
            "1006",
            "Rice",
            "FOOD_BASIC",
            0,
            True,
            VAT_EXEMPTION_REASONS["FOOD"],
        )
        cls._add_hsn_code(
            "0401",
            "Milk and cream",
            "FOOD_BASIC",
            0,
            True,
            VAT_EXEMPTION_REASONS["FOOD"],
        )

        # Infant products
        cls._add_hsn_code(
            "1901",
            "Infant food preparations",
            "INFANT",
            0,
            True,
            VAT_EXEMPTION_REASONS["INFANT"],
        )
        cls._add_hsn_code(
            "3401",
            "Baby soap and cleansing preparations",
            "INFANT",
            0,
            True,
            VAT_EXEMPTION_REASONS["INFANT"],
        )

        # Educational materials
        cls._add_hsn_code(
            "4901",
            "Books, brochures, leaflets",
            "EDUCATION",
            0,
            True,
            VAT_EXEMPTION_REASONS["EDUCATION"],
        )
        cls._add_hsn_code(
            "4902",
            "Newspapers, journals",
            "EDUCATION",
            0,
            True,
            VAT_EXEMPTION_REASONS["EDUCATION"],
        )

        # Standard taxable items
        cls._add_hsn_code(
            "8471",
            "Computers and computer peripherals",
            "ELECTRONICS",
            7.5,
            False,
        )
        cls._add_hsn_code(
            "8517",
            "Telephones and telecommunication equipment",
            "ELECTRONICS",
            7.5,
            False,
        )
        cls._add_hsn_code(
            "8703",
            "Motor cars and vehicles",
            "AUTOMOTIVE",
            7.5,
            False,
        )
        cls._add_hsn_code("9403", "Furniture", "FURNITURE", 7.5, False)
        cls._add_hsn_code("6109", "T-shirts, singlets", "TEXTILES", 7.5, False)

    @classmethod
    def _add_hsn_code(
        cls,
        code: str,
        description: str,
        category: str,
        tax_rate: float,
        is_exempt: bool,
        exemption_reason: str | None = None,
    ) -> None:
        """Add HSN code to database."""
        hsn_code = HSNCode(
            code=code,
            description=description,
            category=category,
            tax_rate=tax_rate,
            is_exempt=is_exempt,
            exemption_reason=exemption_reason,
        )
        cls._hsn_database[code] = hsn_code

    @classmethod
    def get_hsn_code(cls, code: str) -> Optional[HSNCode]:
        """Get HSN code details."""
        cls.initialize()

        # Try exact match first
        hsn = cls._hsn_database.get(code)

        # If not found, try with first 4 digits (chapter level)
        if not hsn and len(code) >= 4:
            hsn = cls._hsn_database.get(code[:4])

        return hsn

    @classmethod
    def is_exempt(cls, hsn_code: str) -> bool:
        """Check if HSN code is VAT exempt."""
        hsn = cls.get_hsn_code(hsn_code)
        return hsn.is_exempt if hsn else False

    @classmethod
    def get_tax_rate(cls, hsn_code: str) -> float:
        """Get tax rate for HSN code."""
        hsn = cls.get_hsn_code(hsn_code)
        return hsn.tax_rate if hsn else 7.5  # Default to standard VAT rate

    @classmethod
    def get_exemption_reason(cls, hsn_code: str) -> Optional[str]:
        """Get exemption reason for HSN code."""
        hsn = cls.get_hsn_code(hsn_code)
        return hsn.exemption_reason if hsn else None

    @classmethod
    def validate_hsn_code(cls, code: str) -> bool:
        """Validate HSN code format (4-8 digits)."""
        return bool(re.match(r"^\d{4,8}$", code))

    @classmethod
    def get_category_hsn_codes(cls, category: str) -> List[HSNCode]:
        """Get all HSN codes in a category."""
        cls.initialize()
        return [
            hsn
            for hsn in cls._hsn_database.values()
            if hsn.category == category
        ]

    @classmethod
    def get_exempt_hsn_codes(cls) -> List[HSNCode]:
        """Get all exempt HSN codes."""
        cls.initialize()
        return [hsn for hsn in cls._hsn_database.values() if hsn.is_exempt]

    @classmethod
    def search_hsn(cls, search_term: str) -> List[HSNCode]:
        """Search HSN codes by term."""
        cls.initialize()
        results = []
        term = search_term.lower()

        for hsn in cls._hsn_database.values():
            if (
                term in hsn.code.lower()
                or term in hsn.description.lower()
                or term in hsn.category.lower()
            ):
                results.append(hsn)

        return results

    @classmethod
    def add_custom_hsn_code(cls, hsn: HSNCode) -> None:
        """Add custom HSN code."""
        if not cls.validate_hsn_code(hsn.code):
            raise ValueError("Invalid HSN code format")
        cls._hsn_database[hsn.code] = hsn

    @classmethod
    def remove_hsn_code(cls, code: str) -> bool:
        """Remove HSN code from database."""
        return cls._hsn_database.pop(code, None) is not None

    @classmethod
    def clear_custom_hsn_codes(cls) -> None:
        """Clear all HSN codes and reinitialize with defaults."""
        cls._hsn_database.clear()
        cls.initialize()

    @classmethod
    def export_hsn_codes(cls) -> List[HSNCode]:
        """Export all HSN codes."""
        cls.initialize()
        return list(cls._hsn_database.values())

    @classmethod
    def import_hsn_codes(cls, codes: List[HSNCode]) -> None:
        """Import HSN codes list."""
        for hsn in codes:
            if cls.validate_hsn_code(hsn.code):
                cls._hsn_database[hsn.code] = hsn

    @classmethod
    def get_statistics(cls) -> Dict[str, any]:
        """Get HSN database statistics."""
        cls.initialize()

        exempt = sum(1 for hsn in cls._hsn_database.values() if hsn.is_exempt)
        taxable = len(cls._hsn_database) - exempt

        categories: Dict[str, int] = {}
        for hsn in cls._hsn_database.values():
            categories[hsn.category] = categories.get(hsn.category, 0) + 1

        return {
            "total": len(cls._hsn_database),
            "exempt": exempt,
            "taxable": taxable,
            "categories": categories,
        }


# Initialize on import
HSNManager.initialize()
