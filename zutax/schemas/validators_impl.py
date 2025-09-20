"""Zutax-native copy of validators."""

import re
from typing import Optional, Tuple
from decimal import Decimal
from ..config.constants import VALIDATION_RULES, VAT_EXEMPT_HSN_CODES

# Re-exported function names preserved to avoid breaking imports


def validate_tin(tin: str) -> Tuple[bool, Optional[str]]:
    if not tin:
        return False, "TIN is required"
    if not tin.isdigit():
        return False, "TIN must contain only digits"
    rules = VALIDATION_RULES["tin"]
    if len(tin) < rules["min_length"]:
        return False, f"TIN must be at least {rules['min_length']} digits"
    if len(tin) > rules["max_length"]:
        return False, f"TIN must not exceed {rules['max_length']} digits"
    if not re.match(rules["pattern"], tin):
        return False, "TIN must contain only digits"
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    if not phone:
        return False, "Phone number is required"
    if not re.match(r"^[\d+]+$", phone):
        return False, "Phone number can only contain digits and +"
    patterns = VALIDATION_RULES["phone"]["patterns"]
    for pattern in patterns:
        if re.match(pattern, phone):
            return True, None
    return (
        False,
        "Invalid phone. Use 08012345678 or +2348012345678",
    )


def validate_hsn_code(hsn_code: str) -> Tuple[bool, Optional[str]]:
    if not hsn_code:
        return False, "HSN/SAC code is required"
    if not hsn_code.isdigit():
        return False, "HSN/SAC code must contain only digits"
    rules = VALIDATION_RULES["hsn_code"]
    if len(hsn_code) < rules["min_length"]:
        return False, (
            f"HSN/SAC code must be at least {rules['min_length']} digits"
        )
    if len(hsn_code) > rules["max_length"]:
        return False, (
            f"HSN/SAC code must not exceed {rules['max_length']} digits"
        )
    if len(hsn_code) % 2 != 0:
        return False, (
            "HSN/SAC code must have even number of digits (4, 6, or 8)"
        )
    if not re.match(rules["pattern"], hsn_code):
        return False, "HSN/SAC code must contain only digits"
    return True, None


def validate_invoice_number(invoice_number: str) -> Tuple[bool, Optional[str]]:
    if not invoice_number:
        return False, "Invoice number is required"
    rules = VALIDATION_RULES["invoice_number"]
    if len(invoice_number) < rules["min_length"]:
        return False, (
            f"Invoice number must be at least {rules['min_length']} characters"
        )
    if len(invoice_number) > rules["max_length"]:
        return False, (
            f"Invoice number must not exceed {rules['max_length']} characters"
        )
    if not re.match(rules["pattern"], invoice_number.upper()):
        return False, (
            "Invoice number can only contain letters, numbers, hyphens, "
            "underscores, and forward slashes"
        )
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    if not email:
        return False, "Email address is required"
    pattern = VALIDATION_RULES["email"]["pattern"]
    if not re.match(pattern, email.lower()):
        return False, "Invalid email address format"
    return True, None


def validate_bank_account(account_number: str) -> Tuple[bool, Optional[str]]:
    if not account_number:
        return False, "Account number is required"
    account_clean = re.sub(r"\D", "", account_number)
    if len(account_clean) != 10:
        return False, "Account number must be 10 digits"
    if not account_clean.isdigit():
        return False, "Account number must contain only digits"
    return True, None


def validate_postal_code(postal_code: str) -> Tuple[bool, Optional[str]]:
    if not postal_code:
        return True, None
    postal_clean = re.sub(r"\D", "", postal_code)
    if len(postal_clean) != 6:
        return False, "Postal code must be 6 digits"
    if not postal_clean.isdigit():
        return False, "Postal code must contain only digits"
    return True, None


def validate_tax_rate(tax_rate: Decimal) -> Tuple[bool, Optional[str]]:
    if tax_rate < 0:
        return False, "Tax rate cannot be negative"
    if tax_rate > 100:
        return False, "Tax rate cannot exceed 100%"
    return True, None


def is_vat_exempt(hsn_code: str) -> bool:
    if not hsn_code:
        return False
    if hsn_code in VAT_EXEMPT_HSN_CODES:
        return True
    hsn_prefix_2 = hsn_code[:2] if len(hsn_code) >= 2 else None
    hsn_prefix_4 = hsn_code[:4] if len(hsn_code) >= 4 else None
    if hsn_prefix_2 and hsn_prefix_2 in VAT_EXEMPT_HSN_CODES:
        return True
    if hsn_prefix_4 and hsn_prefix_4 in VAT_EXEMPT_HSN_CODES:
        return True
    return False


def validate_currency_code(currency: str) -> Tuple[bool, Optional[str]]:
    valid_currencies = ["NGN", "USD", "EUR", "GBP", "XOF"]
    if not currency:
        return False, "Currency code is required"
    if currency.upper() not in valid_currencies:
        return False, (
            "Invalid currency code. Valid codes: "
            + ", ".join(valid_currencies)
        )
    return True, None


def validate_state_code(state_code: str) -> Tuple[bool, Optional[str]]:
    valid_states = [
        "AB",
        "AD",
        "AK",
        "AN",
        "BA",
        "BE",
        "BO",
        "BY",
        "CR",
        "DE",
        "EB",
        "ED",
        "EK",
        "EN",
        "FC",
        "GO",
        "IM",
        "JI",
        "KD",
        "KE",
        "KN",
        "KO",
        "KT",
        "KW",
        "LA",
        "NA",
        "NI",
        "OG",
        "ON",
        "OS",
        "OY",
        "PL",
        "RI",
        "SO",
        "TA",
        "YO",
        "ZA",
    ]
    if not state_code:
        return False, "State code is required"
    if state_code.upper() not in valid_states:
        return False, f"Invalid Nigerian state code: {state_code}"
    return True, None


def validate_business_id(business_id: str) -> Tuple[bool, Optional[str]]:
    if not business_id:
        return False, "Business ID is required"
    if not re.match(r"^[A-Z0-9\-_]+$", business_id.upper()):
        return False, (
            "Business ID can only contain letters, numbers, hyphens, and "
            "underscores"
        )
    if len(business_id) < 3:
        return False, "Business ID must be at least 3 characters"
    if len(business_id) > 50:
        return False, "Business ID must not exceed 50 characters"
    return True, None


def validate_amount(
    amount: Decimal, field_name: str = "Amount"
) -> Tuple[bool, Optional[str]]:
    if amount < 0:
        return False, f"{field_name} cannot be negative"
    if amount.as_tuple().exponent < -2:
        return False, f"{field_name} cannot have more than 2 decimal places"
    return True, None


def validate_quantity(quantity: Decimal) -> Tuple[bool, Optional[str]]:
    if quantity <= 0:
        return False, "Quantity must be greater than zero"
    if quantity.as_tuple().exponent < -3:
        return False, "Quantity cannot have more than 3 decimal places"
    return True, None


class InvoiceValidator:
    """Minimal invoice validator keeping legacy-compatible interface."""

    @staticmethod
    def validate_invoice(invoice) -> dict:
        """Validate an invoice by re-validating its Pydantic model.

        Returns a dict with keys: valid (bool), errors (List[str]),
        warnings (List[str]).
        """
        try:
            # Basic validation - ensure it's a valid Pydantic model instance
            if hasattr(invoice, "model_validate") and hasattr(
                invoice, "model_dump"
            ):
                invoice.model_validate(invoice.model_dump())

            return {"valid": True, "errors": [], "warnings": []}
        except Exception as e:  # pragma: no cover - defensive
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
            }
