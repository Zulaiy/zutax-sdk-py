"""Party (Customer/Supplier) Pydantic models."""

from pydantic import Field, field_validator, EmailStr
from typing import Optional, List
import re
from .base import FIRSBaseModel, StrictBaseModel
from .enums import StateCode, CountryCode


class Address(StrictBaseModel):
    """Address Pydantic model for Nigerian addresses."""
    
    street: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Street address"
    )
    street2: Optional[str] = Field(
        None,
        max_length=200,
        description="Additional street address"
    )
    city: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="City name"
    )
    state_code: StateCode = Field(
        ...,
        description="Nigerian state code"
    )
    lga_code: Optional[str] = Field(
        None,
        pattern=r'^[A-Z0-9\-]+$',
        description="Local Government Area code"
    )
    postal_code: Optional[str] = Field(
        None,
        pattern=r'^\d{6}$',
        description="Nigerian postal code (6 digits)"
    )
    country_code: CountryCode = Field(
        default=CountryCode.NG,
        description="Country code (default: NG)"
    )
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate Nigerian postal code format."""
        if v and not re.match(r'^\d{6}$', v):
            raise ValueError('Postal code must be 6 digits')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "street": "123 Victoria Island",
                "city": "Lagos",
                "state_code": "LA",
                "lga_code": "ETI-OSA",
                "postal_code": "101241",
                "country_code": "NG"
            }
        }
    }


class Contact(FIRSBaseModel):
    """Contact information model."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person name"
    )
    phone: str = Field(
        ...,
        description="Contact phone number"
    )
    email: EmailStr = Field(
        ...,
        description="Contact email address"
    )
    role: Optional[str] = Field(
        None,
        max_length=50,
        description="Contact role/position"
    )
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize Nigerian phone numbers."""
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', v)
        
        # Nigerian phone validation patterns
        if phone.startswith('234'):
            # International format: 234XXXXXXXXXX
            if len(phone) != 13:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+{phone}'
        elif phone.startswith('0'):
            # Local format: 0XXXXXXXXXX
            if len(phone) != 11:
                raise ValueError('Invalid Nigerian phone number format')
            # Convert to international format
            return f'+234{phone[1:]}'
        else:
            raise ValueError('Phone number must start with 0 or 234')


class Party(StrictBaseModel):
    """Party (Customer/Supplier/Billing/Shipping) Pydantic model."""
    
    # Business identification
    business_id: str = Field(
        ...,
        pattern=r'^[A-Z0-9\-]+$',
        min_length=3,
        max_length=50,
        description="Unique business identifier"
    )
    tin: str = Field(
        ...,
        pattern=r'^\d{8,15}$',
        description="Tax Identification Number (8-15 digits)"
    )
    
    # Business details
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Legal business name"
    )
    trade_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Trading/brand name"
    )
    
    # Registration details
    registration_number: Optional[str] = Field(
        None,
        pattern=r'^[A-Z0-9\-/]+$',
        max_length=50,
        description="Company registration number"
    )
    
    # Contact information
    email: EmailStr = Field(
        ...,
        description="Primary email address"
    )
    phone: str = Field(
        ...,
        description="Primary phone number"
    )
    website: Optional[str] = Field(
        None,
        pattern=r'^https?://.+',
        max_length=200,
        description="Company website URL"
    )
    
    # Address (nested Pydantic model)
    address: Address = Field(
        ...,
        description="Business address"
    )
    
    # Additional addresses
    billing_address: Optional[Address] = Field(
        None,
        description="Billing address if different from main address"
    )
    shipping_address: Optional[Address] = Field(
        None,
        description="Shipping address if different from main address"
    )
    
    # VAT registration
    vat_registered: bool = Field(
        default=False,
        description="VAT registration status"
    )
    vat_number: Optional[str] = Field(
        None,
        pattern=r'^[A-Z0-9]+$',
        max_length=20,
        description="VAT registration number"
    )
    
    # Contact persons
    contacts: Optional[List[Contact]] = Field(
        None,
        max_length=10,
        description="List of contact persons"
    )
    
    # Industry classification
    industry_code: Optional[str] = Field(
        None,
        pattern=r'^\d{4,6}$',
        description="Industry classification code"
    )
    
    @field_validator('tin')
    @classmethod
    def validate_tin(cls, v: str) -> str:
        """Validate Nigerian TIN format."""
        if not v.isdigit():
            raise ValueError('TIN must contain only digits')
        if len(v) < 8 or len(v) > 15:
            raise ValueError('TIN must be between 8 and 15 digits')
        return v
    
    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Validate and normalize Nigerian phone numbers."""
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', v)
        
        # Nigerian phone validation patterns
        if phone.startswith('234'):
            # International format: 234XXXXXXXXXX
            if len(phone) != 13:
                raise ValueError('Invalid Nigerian phone number format')
            return f'+{phone}'
        elif phone.startswith('0'):
            # Local format: 0XXXXXXXXXX
            if len(phone) != 11:
                raise ValueError('Invalid Nigerian phone number format')
            # Convert to international format
            return f'+234{phone[1:]}'
        else:
            raise ValueError('Phone number must start with 0 or 234')
    
    @field_validator('vat_number')
    @classmethod
    def validate_vat_number(cls, v: Optional[str], info) -> Optional[str]:
        """Validate VAT number if VAT registered."""
        values = info.data
        if values.get('vat_registered') and not v:
            raise ValueError('VAT number required when VAT registered')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "business_id": "BUS-123456",
                "tin": "12345678",
                "name": "ABC Company Limited",
                "trade_name": "ABC Stores",
                "registration_number": "RC123456",
                "email": "info@abccompany.ng",
                "phone": "08012345678",
                "website": "https://www.abccompany.ng",
                "address": {
                    "street": "123 Victoria Island",
                    "city": "Lagos",
                    "state_code": "LA",
                    "lga_code": "ETI-OSA",
                    "postal_code": "101241",
                    "country_code": "NG"
                },
                "vat_registered": True,
                "vat_number": "VAT123456"
            }
        }
    }