"""Constants for FIRS E-Invoice SDK (Zutax namespace)."""

from decimal import Decimal
from typing import Dict, Any

# API Configuration
API_VERSION = "v1"
DEFAULT_BASE_URL = "https://api.firs.gov.ng/api/v1"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Tax Rates
VAT_RATE = Decimal("7.5")  # Nigerian VAT rate
WITHHOLDING_TAX_RATE = Decimal("5.0")
COMPANY_INCOME_TAX_RATE = Decimal("30.0")

# Tax Categories
TAX_CATEGORIES = {
    "STANDARD_VAT": "VAT",
    "REDUCED_VAT": "VAT",
    "ZERO_VAT": "VAT",
    "ALCOHOL_EXCISE_TAX": "EXCISE",
    "TOBACCO_EXCISE_TAX": "EXCISE",
    "FUEL_EXCISE_TAX": "EXCISE",
    "IMPORT_DUTY": "CUSTOMS",
    "EXPORT_DUTY": "CUSTOMS",
    "WITHHOLDING_TAX": "WITHHOLDING",
}

# VAT Exemption Reasons
VAT_EXEMPTION_REASONS = {
    "MEDICAL": (
        "Medical equipment and pharmaceuticals - VAT exempt under "
        "Nigerian law"
    ),
    "FOOD": "Basic food items - VAT exempt under Nigerian law",
    "INFANT": (
        "Infant and baby products - VAT exempt under Nigerian law"
    ),
    "EDUCATION": (
        "Educational materials and books - VAT exempt under Nigerian law"
    ),
    "AGRICULTURE": (
        "Agricultural products and equipment - VAT exempt under "
        "Nigerian law"
    ),
}

# Default Configuration
DEFAULT_CONFIG = {
    "DEFAULT_TAX_RATE": VAT_RATE,
    "DEFAULT_CURRENCY": "NGN",
    "DEFAULT_TIMEOUT": DEFAULT_TIMEOUT,
    "DEFAULT_MAX_RETRIES": DEFAULT_MAX_RETRIES,
}

# API Endpoints
ENDPOINTS = {
    # Invoice endpoints
    "validate": "/invoice/validate",
    "submit": "/invoice/submit",
    "status": "/invoice/status/{irn}",
    "cancel": "/invoice/cancel",
    "batch_validate": "/invoice/batch/validate",
    "batch_submit": "/invoice/batch/submit",
    
    # Resource endpoints
    "invoice_types": "/invoice/resources/invoice-types",
    "tax_categories": "/invoice/resources/tax-categories",
    "vat_exemptions": "/invoice/resources/vat-exemptions",
    "product_codes": "/invoice/resources/product-codes",
    "service_codes": "/invoice/resources/service-codes",
    "states": "/invoice/resources/states",
    "lgas": "/invoice/resources/lgas",
    "currencies": "/invoice/resources/currencies",
    "units": "/invoice/resources/units-of-measure",
}

# HSN Code Categories
HSN_CATEGORIES = {
    "FOOD": {
        "codes": [
            "01", "02", "03", "04", "05", "06", "07", "08",
            "09", "10", "11", "12", "13", "14", "15", "16",
            "17", "18", "19", "20", "21", "22", "23"
        ],
        "description": "Food and agricultural products",
        "vat_exempt": True,
    },
    "MEDICAL": {
        "codes": ["30", "9018", "9019", "9020", "9021", "9022"],
        "description": "Medical and pharmaceutical products",
        "vat_exempt": True,
    },
    "EDUCATION": {
        "codes": ["49"],
        "description": "Educational materials and books",
        "vat_exempt": True,
    },
    "INFANT": {
        "codes": ["3401", "3402", "3403", "3404", "3405", "3406", "3407"],
        "description": "Infant and baby products",
        "vat_exempt": True,
    },
    "ELECTRONICS": {
        "codes": ["84", "85"],
        "description": "Electronics and electrical equipment",
        "vat_exempt": False,
    },
    "TEXTILES": {
        "codes": [
            "50", "51", "52", "53", "54", "55", "56", "57", "58",
            "59", "60", "61", "62", "63"
        ],
        "description": "Textiles and clothing",
        "vat_exempt": False,
    },
    "MACHINERY": {
        "codes": ["84", "85", "86", "87", "88", "89", "90"],
        "description": "Machinery and equipment",
        "vat_exempt": False,
    },
    "SERVICES": {
        "codes": ["99"],
        "description": "Services",
        "vat_exempt": False,
    },
}

# VAT Exempt HSN Codes (Nigerian specific)
VAT_EXEMPT_HSN_CODES = [
    # Agricultural products (Chapter 01-24)
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24",
    
    # Medical equipment and pharmaceuticals
    "30",  # Pharmaceutical products
    "9018",  # Medical instruments
    "9019",  # Mechano-therapy appliances
    "9020",  # Breathing appliances
    "9021",  # Orthopedic appliances
    "9022",  # X-ray apparatus
    
    # Educational materials
    "49",  # Books and newspapers
    
    # Baby and infant products
    "3401", "3402", "3403", "3404", "3405", "3406", "3407",
    
    # Basic food items
    "1001",  # Wheat
    "1002",  # Rye
    "1003",  # Barley
    "1004",  # Oats
    "1005",  # Maize
    "1006",  # Rice
    "1007",  # Sorghum
    "1008",  # Other cereals
]

# Invoice Number Patterns
INVOICE_NUMBER_PATTERNS = {
    "standard": r"^INV-\d{4}-\d{6}$",  # INV-2024-000001
    "credit": r"^CRN-\d{4}-\d{6}$",   # CRN-2024-000001
    "debit": r"^DBN-\d{4}-\d{6}$",    # DBN-2024-000001
    "import": r"^IMP-\d{4}-\d{6}$",   # IMP-2024-000001
    "export": r"^EXP-\d{4}-\d{6}$",   # EXP-2024-000001
}

# Error Messages
ERROR_MESSAGES = {
    "INVALID_TIN": "Invalid Tax Identification Number format",
    "INVALID_PHONE": "Invalid Nigerian phone number format",
    "INVALID_HSN": "Invalid HSN/SAC code format",
    "INVALID_INVOICE_NUMBER": "Invalid invoice number format",
    "MISSING_LINE_ITEMS": "Invoice must have at least one line item",
    "INVALID_TAX_RATE": "Invalid tax rate",
    "AUTHENTICATION_FAILED": "API authentication failed",
    "SUBMISSION_FAILED": "Invoice submission failed",
    "VALIDATION_FAILED": "Invoice validation failed",
}

# Success Messages
SUCCESS_MESSAGES = {
    "INVOICE_VALIDATED": "Invoice validated successfully",
    "INVOICE_SUBMITTED": "Invoice submitted successfully",
    "INVOICE_CANCELLED": "Invoice cancelled successfully",
    "QR_GENERATED": "QR code generated successfully",
    "SIGNATURE_CREATED": "Digital signature created successfully",
}

# QR Code Configuration
QR_CODE_CONFIG = {
    "version": 1,
    "error_correction": "M",  # L, M, Q, H
    "box_size": 10,
    "border": 4,
    "default_format": "PNG",
    "max_data_size": 4296,  # Maximum bytes for QR code data
}

# Digital Signature Configuration
SIGNATURE_CONFIG = {
    "algorithm": "RSA",
    "key_size": 2048,
    "hash_algorithm": "SHA256",
    "encoding": "base64",
}

# Validation Rules
VALIDATION_RULES = {
    "tin": {
        "min_length": 8,
        "max_length": 11,
        "pattern": r"^\d{8,11}$",
    },
    "phone": {
        "patterns": [
            r"^\+234[789][01]\d{8}$",  # International format
            r"^0[789][01]\d{8}$",  # Local format
        ],
    },
    "invoice_number": {
        "min_length": 3,
        "max_length": 50,
        "pattern": r"^[A-Z0-9\-/_]+$",
    },
    "hsn_code": {
        "min_length": 4,
        "max_length": 8,
        "pattern": r"^\d{4,8}$",
    },
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    },
}

# HTTP Headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "FIRS-EInvoice-Python-SDK/1.0.0",
}

# Cache Keys
CACHE_KEYS = {
    "vat_exemptions": "firs:resources:vat_exemptions",
    "product_codes": "firs:resources:product_codes",
    "service_codes": "firs:resources:service_codes",
    "states": "firs:resources:states",
    "lgas": "firs:resources:lgas:{state_code}",
    "invoice_types": "firs:resources:invoice_types",
    "tax_categories": "firs:resources:tax_categories",
}

# Date Formats
DATE_FORMATS = {
    "invoice": "%Y-%m-%d",
    "datetime": "%Y-%m-%dT%H:%M:%S",
    "timestamp": "%Y-%m-%dT%H:%M:%S.%fZ",
    "irn": "%Y%m%d",
}

# File Extensions
ALLOWED_EXTENSIONS = {
    "images": [".png", ".jpg", ".jpeg", ".svg"],
    "documents": [".pdf", ".json", ".xml"],
    "keys": [".pem", ".key", ".crt", ".cer"],
}

# Limits
LIMITS = {
    "max_line_items": 1000,
    "max_batch_size": 100,
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "max_description_length": 500,
    "max_notes_length": 1000,
}

# Nigerian States and LGAs mapping (simplified)
STATES_LGAS: Dict[str, Any] = {
    "LA": {
        "name": "Lagos",
        "lgas": [
            "Agege",
            "Ajeromi-Ifelodun",
            "Alimosho",
            "Amuwo-Odofin",
            "Apapa",
            "Badagry",
            "Epe",
            "Eti-Osa",
            "Ibeju-Lekki",
            "Ifako-Ijaiye",
            "Ikeja",
            "Ikorodu",
            "Kosofe",
            "Lagos Island",
            "Lagos Mainland",
            "Mushin",
            "Ojo",
            "Oshodi-Isolo",
            "Shomolu",
            "Surulere",
        ],
    },
    "FC": {
        "name": "Federal Capital Territory",
        "lgas": [
            "Abaji",
            "Abuja Municipal",
            "Bwari",
            "Gwagwalada",
            "Kuje",
            "Kwali",
        ],
    },
    # Add more states as needed
}
