"""Custom validators for Nigerian-specific requirements."""

import re
from typing import Optional, List, Tuple
from decimal import Decimal
from ..config.constants import VALIDATION_RULES, VAT_EXEMPT_HSN_CODES


def validate_tin(tin: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Nigerian Tax Identification Number.
    
    Args:
        tin: Tax Identification Number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tin:
        return False, "TIN is required"
    
    # Don't allow non-digit characters in original string
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
    """
    Validate Nigerian phone number.
    
    Args:
        phone: Phone number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Don't allow any characters other than digits and +
    if not re.match(r'^[\d+]+$', phone):
        return False, "Phone number can only contain digits and +"
    
    patterns = VALIDATION_RULES["phone"]["patterns"]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True, None
    
    return False, "Invalid Nigerian phone number format. Use format: 08012345678 or +2348012345678"


def validate_hsn_code(hsn_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate HSN/SAC code.
    
    Args:
        hsn_code: HSN or SAC code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not hsn_code:
        return False, "HSN/SAC code is required"
    
    # Don't allow non-digit characters
    if not hsn_code.isdigit():
        return False, "HSN/SAC code must contain only digits"
    
    rules = VALIDATION_RULES["hsn_code"]
    if len(hsn_code) < rules["min_length"]:
        return False, f"HSN/SAC code must be at least {rules['min_length']} digits"
    
    if len(hsn_code) > rules["max_length"]:
        return False, f"HSN/SAC code must not exceed {rules['max_length']} digits"
    
    # HSN codes should be even length (2, 4, 6, or 8 digits)
    if len(hsn_code) % 2 != 0:
        return False, "HSN/SAC code must have even number of digits (4, 6, or 8)"
    
    if not re.match(rules["pattern"], hsn_code):
        return False, "HSN/SAC code must contain only digits"
    
    return True, None


def validate_invoice_number(invoice_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate invoice number format.
    
    Args:
        invoice_number: Invoice number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not invoice_number:
        return False, "Invoice number is required"
    
    rules = VALIDATION_RULES["invoice_number"]
    
    if len(invoice_number) < rules["min_length"]:
        return False, f"Invoice number must be at least {rules['min_length']} characters"
    
    if len(invoice_number) > rules["max_length"]:
        return False, f"Invoice number must not exceed {rules['max_length']} characters"
    
    if not re.match(rules["pattern"], invoice_number.upper()):
        return False, "Invoice number can only contain letters, numbers, hyphens, underscores, and forward slashes"
    
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address.
    
    Args:
        email: Email address
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"
    
    pattern = VALIDATION_RULES["email"]["pattern"]
    
    if not re.match(pattern, email.lower()):
        return False, "Invalid email address format"
    
    return True, None


def validate_bank_account(account_number: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Nigerian bank account number.
    
    Args:
        account_number: Bank account number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not account_number:
        return False, "Account number is required"
    
    # Remove any non-digit characters
    account_clean = re.sub(r'\D', '', account_number)
    
    # Nigerian bank accounts are typically 10 digits
    if len(account_clean) != 10:
        return False, "Account number must be 10 digits"
    
    if not account_clean.isdigit():
        return False, "Account number must contain only digits"
    
    return True, None


def validate_postal_code(postal_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Nigerian postal code.
    
    Args:
        postal_code: Postal code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not postal_code:
        return True, None  # Postal code is optional
    
    # Remove any non-digit characters
    postal_clean = re.sub(r'\D', '', postal_code)
    
    # Nigerian postal codes are 6 digits
    if len(postal_clean) != 6:
        return False, "Postal code must be 6 digits"
    
    if not postal_clean.isdigit():
        return False, "Postal code must contain only digits"
    
    return True, None


def validate_tax_rate(tax_rate: Decimal) -> Tuple[bool, Optional[str]]:
    """
    Validate tax rate.
    
    Args:
        tax_rate: Tax rate percentage
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if tax_rate < 0:
        return False, "Tax rate cannot be negative"
    
    if tax_rate > 100:
        return False, "Tax rate cannot exceed 100%"
    
    return True, None


def is_vat_exempt(hsn_code: str) -> bool:
    """
    Check if HSN code is VAT exempt.
    
    Args:
        hsn_code: HSN code to check
        
    Returns:
        True if VAT exempt, False otherwise
    """
    if not hsn_code:
        return False
    
    # Check exact match first
    if hsn_code in VAT_EXEMPT_HSN_CODES:
        return True
    
    # Check prefix match (first 2 or 4 digits)
    hsn_prefix_2 = hsn_code[:2] if len(hsn_code) >= 2 else None
    hsn_prefix_4 = hsn_code[:4] if len(hsn_code) >= 4 else None
    
    if hsn_prefix_2 and hsn_prefix_2 in VAT_EXEMPT_HSN_CODES:
        return True
    
    if hsn_prefix_4 and hsn_prefix_4 in VAT_EXEMPT_HSN_CODES:
        return True
    
    return False


def validate_currency_code(currency: str) -> Tuple[bool, Optional[str]]:
    """
    Validate currency code (ISO 4217).
    
    Args:
        currency: Currency code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_currencies = ["NGN", "USD", "EUR", "GBP", "XOF"]
    
    if not currency:
        return False, "Currency code is required"
    
    if currency.upper() not in valid_currencies:
        return False, f"Invalid currency code. Valid codes: {', '.join(valid_currencies)}"
    
    return True, None


def validate_state_code(state_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Nigerian state code.
    
    Args:
        state_code: State code
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_states = [
        "AB", "AD", "AK", "AN", "BA", "BE", "BO", "BY", "CR", "DE",
        "EB", "ED", "EK", "EN", "FC", "GO", "IM", "JI", "KD", "KE",
        "KN", "KO", "KT", "KW", "LA", "NA", "NI", "OG", "ON", "OS",
        "OY", "PL", "RI", "SO", "TA", "YO", "ZA"
    ]
    
    if not state_code:
        return False, "State code is required"
    
    if state_code.upper() not in valid_states:
        return False, f"Invalid Nigerian state code: {state_code}"
    
    return True, None


def validate_business_id(business_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate business ID format.
    
    Args:
        business_id: Business identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not business_id:
        return False, "Business ID is required"
    
    # Business ID should be alphanumeric with hyphens and underscores allowed
    if not re.match(r'^[A-Z0-9\-_]+$', business_id.upper()):
        return False, "Business ID can only contain letters, numbers, hyphens, and underscores"
    
    if len(business_id) < 3:
        return False, "Business ID must be at least 3 characters"
    
    if len(business_id) > 50:
        return False, "Business ID must not exceed 50 characters"
    
    return True, None


def validate_amount(amount: Decimal, field_name: str = "Amount") -> Tuple[bool, Optional[str]]:
    """
    Validate monetary amount.
    
    Args:
        amount: Amount to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount < 0:
        return False, f"{field_name} cannot be negative"
    
    # Check decimal places (max 2 for currency)
    if amount.as_tuple().exponent < -2:
        return False, f"{field_name} cannot have more than 2 decimal places"
    
    return True, None


def validate_quantity(quantity: Decimal) -> Tuple[bool, Optional[str]]:
    """
    Validate quantity.
    
    Args:
        quantity: Quantity to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if quantity <= 0:
        return False, "Quantity must be greater than zero"
    
    # Check decimal places (max 3 for quantity)
    if quantity.as_tuple().exponent < -3:
        return False, "Quantity cannot have more than 3 decimal places"
    
    return True, None


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0
    
    def add_error(self, field: str, message: str):
        """Add validation error."""
        self.errors.append(f"{field}: {message}")
    
    def add_warning(self, field: str, message: str):
        """Add validation warning."""
        self.warnings.append(f"{field}: {message}")
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


class InvoiceValidator:
    """Invoice validation utilities."""
    
    @staticmethod
    def validate_invoice(invoice) -> dict:
        """Validate an invoice instance."""
        try:
            # Basic validation - invoice should be a valid Pydantic model
            if hasattr(invoice, 'model_validate'):
                # Re-validate the model
                invoice.model_validate(invoice.model_dump())
            
            return {
                'valid': True,
                'errors': [],
                'warnings': []
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [{'field': 'invoice', 'message': str(e), 'code': 'VALIDATION_ERROR'}],
                'warnings': []
            }