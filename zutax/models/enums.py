"""Enumeration types for Zutax models."""

from enum import Enum


class InvoiceType(str, Enum):
	STANDARD = "STANDARD"
	CREDIT = "CREDIT"
	DEBIT = "DEBIT"
	IMPORT = "IMPORT"
	EXPORT = "EXPORT"
	SELF_BILLED = "SELF_BILLED"
	SIMPLIFIED = "SIMPLIFIED"


class InvoiceStatus(str, Enum):
	DRAFT = "DRAFT"
	VALIDATED = "VALIDATED"
	SUBMITTED = "SUBMITTED"
	ACCEPTED = "ACCEPTED"
	REJECTED = "REJECTED"
	CANCELLED = "CANCELLED"


class TaxCategory(str, Enum):
	VAT = "VAT"
	EXCISE = "EXCISE"
	CUSTOMS = "CUSTOMS"
	WITHHOLDING = "WITHHOLDING"
	OTHER = "OTHER"


class PaymentMethod(str, Enum):
	CASH = "CASH"
	BANK_TRANSFER = "BANK_TRANSFER"
	CARD = "CARD"
	CHEQUE = "CHEQUE"
	MOBILE_MONEY = "MOBILE_MONEY"
	OTHER = "OTHER"


class Currency(str, Enum):
	NGN = "NGN"
	USD = "USD"
	EUR = "EUR"
	GBP = "GBP"
	XOF = "XOF"


class StateCode(str, Enum):
	AB = "AB"
	AD = "AD"
	AK = "AK"
	AN = "AN"
	BA = "BA"
	BE = "BE"
	BO = "BO"
	BY = "BY"
	CR = "CR"
	DE = "DE"
	EB = "EB"
	ED = "ED"
	EK = "EK"
	EN = "EN"
	FC = "FC"
	GO = "GO"
	IM = "IM"
	JI = "JI"
	KD = "KD"
	KE = "KE"
	KN = "KN"
	KO = "KO"
	KT = "KT"
	KW = "KW"
	LA = "LA"
	NA = "NA"
	NI = "NI"
	OG = "OG"
	ON = "ON"
	OS = "OS"
	OY = "OY"
	PL = "PL"
	RI = "RI"
	SO = "SO"
	TA = "TA"
	YO = "YO"
	ZA = "ZA"


class CountryCode(str, Enum):
	NG = "NG"
	US = "US"
	GB = "GB"
	FR = "FR"
	DE = "DE"
	CN = "CN"
	IN = "IN"
	ZA = "ZA"
	GH = "GH"
	KE = "KE"


class UnitOfMeasure(str, Enum):
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
