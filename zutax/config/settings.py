"""Zutax configuration settings using Pydantic Settings."""

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any
from functools import lru_cache
from pathlib import Path
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_CACHE_TTL,
)


class BusinessContext(BaseSettings):
    """Business context configuration."""
    business_id: str = Field(
        ..., description="Unique business identifier"
    )
    business_name: str = Field(
        ..., description="Legal business name"
    )
    tin: str = Field(
        ..., pattern=r"^\d{8,15}$",
        description="Tax Identification Number",
    )
    vat_number: Optional[str] = Field(
        None, description="VAT registration number"
    )
    email: str = Field(
        ..., description="Business email"
    )
    phone: str = Field(
        ..., description="Business phone"
    )
    address_street: str = Field(
        ..., description="Street address"
    )
    address_city: str = Field(
        ..., description="City"
    )
    address_state: str = Field(
        ..., description="State code"
    )
    address_postal: Optional[str] = Field(
        None, description="Postal code"
    )

    model_config = SettingsConfigDict(
        env_prefix="FIRS_BUSINESS_", case_sensitive=False
    )


class QRCustomization(BaseSettings):
    """QR code customization settings."""

    format: str = Field(
        default="PNG",
        pattern=r"^(PNG|SVG|BASE64|BUFFER)$",
        description="QR code output format",
    )
    size: int = Field(
        default=300, ge=100, le=1000,
        description="QR code size in pixels",
    )
    margin: int = Field(
        default=4, ge=0, le=10, description="QR code margin"
    )
    dark_color: str = Field(
        default="#000000",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Dark module color",
    )
    light_color: str = Field(
        default="#FFFFFF",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Light module color",
    )
    logo_path: Optional[str] = Field(
        None, description="Path to logo image"
    )
    logo_size: Optional[int] = Field(
        None, ge=20, le=200, description="Logo size in pixels"
    )

    model_config = SettingsConfigDict(
        env_prefix="FIRS_QR_", case_sensitive=False
    )


class ZutaxConfig(BaseSettings):
    """Main Zutax configuration using Pydantic Settings."""

    # API Configuration
    api_key: SecretStr = Field(
        ..., description="FIRS API key"
    )
    api_secret: SecretStr = Field(
        ..., description="FIRS API secret"
    )
    base_url: str = Field(
        default=DEFAULT_BASE_URL, description="FIRS API base URL"
    )

    # Business Information
    business_id: str = Field(
        ..., description="Business ID"
    )
    business_name: str = Field(
        ..., description="Business name"
    )
    tin: str = Field(
        ..., pattern=r"^\d{8,15}$",
        description="Tax Identification Number",
    )
    service_id: Optional[str] = Field(
        None, description="FIRS-assigned Service ID (8 characters)"
    )

    # Operational Settings
    timeout: int = Field(
        default=DEFAULT_TIMEOUT, ge=5, le=120,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES, ge=0, le=10,
        description="Maximum number of retry attempts",
    )
    retry_delay: int = Field(
        default=1000, ge=100, le=10000,
        description="Retry delay in milliseconds",
    )
    cache_ttl: int = Field(
        default=DEFAULT_CACHE_TTL, ge=0,
        description="Cache TTL in seconds",
    )
    verify_ssl: bool = Field(
        default=True, description="Verify SSL certificates"
    )

    # Output Configuration
    output_dir: str = Field(
        default="./output",
        description="Output directory for generated files",
    )
    log_level: str = Field(
        default="INFO",
        pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level",
    )
    log_file: Optional[str] = Field(
        None, description="Log file path"
    )

    # Feature Flags
    enable_caching: bool = Field(
        default=True, description="Enable response caching"
    )
    enable_retry: bool = Field(
        default=True,
        description="Enable automatic retry on failure",
    )
    enable_validation: bool = Field(
        default=True,
        description="Enable local validation before API calls",
    )
    debug_mode: bool = Field(
        default=False, description="Enable debug mode"
    )

    # Cryptographic Settings
    private_key_path: Optional[str] = Field(
        None, description="Path to private key for signing"
    )
    certificate_path: Optional[str] = Field(
        None, description="Path to certificate"
    )
    key_password: Optional[SecretStr] = Field(
        None, description="Private key password"
    )
    firs_public_key: Optional[str] = Field(
        None, description="FIRS public key (Base64-encoded PEM)"
    )
    firs_certificate: Optional[str] = Field(
        None, description="FIRS certificate (Base64-encoded)"
    )

    # Proxy Configuration
    proxy_url: Optional[str] = Field(
        None, description="HTTP proxy URL"
    )
    proxy_username: Optional[str] = Field(
        None, description="Proxy username"
    )
    proxy_password: Optional[SecretStr] = Field(
        None, description="Proxy password"
    )

    # Additional Settings
    user_agent: str = Field(
        default="FIRS-EInvoice-Python-SDK/1.0.0",
        description="User agent string",
    )
    max_batch_size: int = Field(
        default=100, ge=1, le=1000,
        description="Maximum batch size for bulk operations",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="FIRS_",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("output_dir")
    @classmethod
    def create_output_dir(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @field_validator("private_key_path", "certificate_path")
    @classmethod
    def validate_file_path(cls, v: Optional[str]) -> Optional[str]:
        if v and not Path(v).exists():
            raise ValueError(f"File not found: {v}")
        return v

    def get_api_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key.get_secret_value(),
            "x-api-secret": self.api_secret.get_secret_value(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def get_proxy_config(self) -> Optional[Dict[str, Any]]:
        if not self.proxy_url:
            return None
        config = {"http": self.proxy_url, "https": self.proxy_url}
        if self.proxy_username and self.proxy_password:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(self.proxy_url)
            auth = (
                f"{self.proxy_username}:"
                f"{self.proxy_password.get_secret_value()}"
            )
            netloc = f"{auth}@{parsed.netloc}"
            auth_url = urlunparse(
                (
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
            config = {"http": auth_url, "https": auth_url}
        return config


class RuntimeConfig:
    """Runtime configuration manager for Zutax."""

    def __init__(self):
        self._config: Optional[ZutaxConfig] = None
        self._business_context: Optional[BusinessContext] = None
        self._qr_customization: Optional[QRCustomization] = None
        self._app_settings: Dict[str, Any] = {}

    def get_config(self) -> ZutaxConfig:
        if not self._config:
            self._config = ZutaxConfig()
        return self._config

    def update_config(self, **kwargs) -> None:
        if not self._config:
            self._config = ZutaxConfig(**kwargs)
        else:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

    def set_business_context(self, context: BusinessContext) -> None:
        self._business_context = context

    def get_business_context(self) -> Optional[BusinessContext]:
        return self._business_context

    def set_qr_customization(self, customization: QRCustomization) -> None:
        self._qr_customization = customization

    def get_qr_customization(self) -> Optional[QRCustomization]:
        return self._qr_customization

    def set_app_settings(self, settings: Dict[str, Any]) -> None:
        self._app_settings.update(settings)

    def get_app_settings(self) -> Dict[str, Any]:
        return self._app_settings.copy()


_runtime_config = RuntimeConfig()


@lru_cache()
def get_config() -> ZutaxConfig:
    return _runtime_config.get_config()


def update_config(**kwargs) -> None:
    _runtime_config.update_config(**kwargs)
    get_config.cache_clear()


def get_business_context() -> Optional[BusinessContext]:
    return _runtime_config.get_business_context()


def set_business_context(context: BusinessContext) -> None:
    _runtime_config.set_business_context(context)


def get_qr_customization() -> Optional[QRCustomization]:
    return _runtime_config.get_qr_customization()


def set_qr_customization(customization: QRCustomization) -> None:
    _runtime_config.set_qr_customization(customization)
