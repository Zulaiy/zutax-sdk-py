"""Party (Customer/Supplier) Pydantic models for Zutax."""

from pydantic import Field, field_validator, EmailStr
from typing import Optional, List
import re
from .base import FIRSBaseModel, StrictBaseModel
from .enums import StateCode, CountryCode


class Address(StrictBaseModel):
    street: str = Field(..., min_length=1, max_length=200, description="Street address")
    street2: Optional[str] = Field(None, max_length=200, description="Additional street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state_code: StateCode = Field(..., description="Nigerian state code")
    lga_code: Optional[str] = Field(None, pattern=r'^[A-Z0-9\-]+$', description="LGA code")
    postal_code: Optional[str] = Field(None, pattern=r'^\d{6}$', description="Postal code")
    country_code: CountryCode = Field(default=CountryCode.NG, description="Country code")

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r'^\d{6}$', v):
            raise ValueError('Postal code must be 6 digits')
        return v


class Contact(FIRSBaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Contact person name")
    phone: str = Field(..., description="Contact phone number")
    email: EmailStr = Field(..., description="Contact email address")
    role: Optional[str] = Field(None, max_length=50, description="Contact role/position")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        phone = re.sub(r'\D', '', v)
        if phone.startswith('234'):
            if len(phone) != 13:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+{phone}'
        elif phone.startswith('0'):
            if len(phone) != 11:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+234{phone[1:]}'
        else:
            raise ValueError('Phone number must start with 0 or 234')


class Party(StrictBaseModel):
    business_id: str = Field(
        ..., pattern=r'^[A-Z0-9\-]+$', min_length=3, max_length=50, description="Business ID"
    )
    tin: str = Field(..., pattern=r'^\d{8,15}$', description="Tax Identification Number")
    name: str = Field(..., min_length=1, max_length=200, description="Legal business name")
    trade_name: Optional[str] = Field(None, max_length=200, description="Trading/brand name")
    registration_number: Optional[str] = Field(
        None, pattern=r'^[A-Z0-9\-/]+$', max_length=50, description="Company registration number"
    )
    email: EmailStr = Field(..., description="Primary email address")
    phone: str = Field(..., description="Primary phone number")
    website: Optional[str] = Field(None, pattern=r'^https?://.+', max_length=200, description="Website")
    address: Address = Field(..., description="Business address")
    billing_address: Optional[Address] = Field(None, description="Billing address")
    shipping_address: Optional[Address] = Field(None, description="Shipping address")
    vat_registered: bool = Field(default=False, description="VAT registration status")
    vat_number: Optional[str] = Field(None, pattern=r'^[A-Z0-9]+$', max_length=20, description="VAT number")
    contacts: Optional[List[Contact]] = Field(None, max_length=10, description="Contacts")
    industry_code: Optional[str] = Field(None, pattern=r'^\d{4,6}$', description="Industry code")

    @field_validator('tin')
    @classmethod
    def validate_tin(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('TIN must contain only digits')
        if len(v) < 8 or len(v) > 15:
            raise ValueError('TIN must be between 8 and 15 digits')
        return v

    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        phone = re.sub(r'\D', '', v)
        if phone.startswith('234'):
            if len(phone) != 13:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+{phone}'
        elif phone.startswith('0'):
            if len(phone) != 11:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+234{phone[1:]}'
        else:
            raise ValueError('Phone number must start with 0 or 234')

    @field_validator('vat_number')
    @classmethod
    def validate_vat_number(cls, v: Optional[str], info) -> Optional[str]:
        if info.data.get('vat_registered') and not v:
            raise ValueError('VAT number required when VAT registered')
        return v
