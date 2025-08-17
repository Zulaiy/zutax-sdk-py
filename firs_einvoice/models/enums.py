"""Enumeration types for FIRS E-Invoice models."""

from enum import Enum


class InvoiceType(str, Enum):
    """Invoice type enumeration."""
    STANDARD = "STANDARD"
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    SELF_BILLED = "SELF_BILLED"
    SIMPLIFIED = "SIMPLIFIED"


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class TaxCategory(str, Enum):
    """Tax category enumeration."""
    VAT = "VAT"
    EXCISE = "EXCISE"
    CUSTOMS = "CUSTOMS"
    WITHHOLDING = "WITHHOLDING"
    OTHER = "OTHER"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"
    CHEQUE = "CHEQUE"
    MOBILE_MONEY = "MOBILE_MONEY"
    OTHER = "OTHER"


class Currency(str, Enum):
    """Currency codes (ISO 4217)."""
    NGN = "NGN"  # Nigerian Naira
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    XOF = "XOF"  # West African CFA franc


class StateCode(str, Enum):
    """Nigerian state codes."""
    AB = "AB"  # Abia
    AD = "AD"  # Adamawa
    AK = "AK"  # Akwa Ibom
    AN = "AN"  # Anambra
    BA = "BA"  # Bauchi
    BE = "BE"  # Benue
    BO = "BO"  # Borno
    BY = "BY"  # Bayelsa
    CR = "CR"  # Cross River
    DE = "DE"  # Delta
    EB = "EB"  # Ebonyi
    ED = "ED"  # Edo
    EK = "EK"  # Ekiti
    EN = "EN"  # Enugu
    FC = "FC"  # Federal Capital Territory
    GO = "GO"  # Gombe
    IM = "IM"  # Imo
    JI = "JI"  # Jigawa
    KD = "KD"  # Kaduna
    KE = "KE"  # Kebbi
    KN = "KN"  # Kano
    KO = "KO"  # Kogi
    KT = "KT"  # Katsina
    KW = "KW"  # Kwara
    LA = "LA"  # Lagos
    NA = "NA"  # Nasarawa
    NI = "NI"  # Niger
    OG = "OG"  # Ogun
    ON = "ON"  # Ondo
    OS = "OS"  # Osun
    OY = "OY"  # Oyo
    PL = "PL"  # Plateau
    RI = "RI"  # Rivers
    SO = "SO"  # Sokoto
    TA = "TA"  # Taraba
    YO = "YO"  # Yobe
    ZA = "ZA"  # Zamfara


class CountryCode(str, Enum):
    """Country codes (ISO 3166-1 alpha-2)."""
    NG = "NG"  # Nigeria
    US = "US"  # United States
    GB = "GB"  # United Kingdom
    FR = "FR"  # France
    DE = "DE"  # Germany
    CN = "CN"  # China
    IN = "IN"  # India
    ZA = "ZA"  # South Africa
    GH = "GH"  # Ghana
    KE = "KE"  # Kenya


class UnitOfMeasure(str, Enum):
    """Units of measurement."""
    PIECE = "PCE"
    KILOGRAM = "KG"
    GRAM = "G"
    LITRE = "L"
    MILLILITRE = "ML"
    METRE = "M"
    CENTIMETRE = "CM"
    SQUARE_METRE = "M2"
    CUBIC_METRE = "M3"
    HOUR = "HR"
    DAY = "DAY"
    MONTH = "MON"
    YEAR = "YR"
    BOX = "BOX"
    PACK = "PCK"
    DOZEN = "DZ"
    UNIT = "UNIT"