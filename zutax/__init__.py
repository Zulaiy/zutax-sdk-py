"""Zutax (by Zulaiy) – Python SDK for FIRS e-Invoicing.

Public API providing Zutax* class names while reusing the current
implementation. This enables a clean rename without breaking internals
in one step.
"""

from .client import ZutaxClient  # noqa: F401
from .processors import InvoiceProcessor, ProcessingResult  # noqa: F401

# Native Zutax configuration
from .config import ZutaxConfig  # noqa: F401

# Builders from Zutax implementation
from .builders import InvoiceBuilder, LineItemBuilder  # noqa: F401

# Managers (native Zutax)
from .managers import (  # noqa: F401
    HSNManager,
    HSNCode,
    TaxManager,
    TaxCalculation as SimpleTaxCalculation,
    TaxBreakdown as SimpleTaxBreakdown,
)

# API exports (Zutax)
from .api import (  # noqa: F401
    ZutaxAPIClient,
    api_client as zutax_api_client,
    APIError as ZutaxAPIError,
    APIResponse as ZutaxAPIResponse,
    InvoiceAPI,
    FIRSValidationResponse,
    InvoiceSubmissionResult,
    ResourceAPI,
)

# Public models should come from Zutax implementations
from .models import (  # noqa: F401
    Party,
    Address,
    LineItem,
    Invoice,
    PaymentDetails,
)

# Native crypto exports (signer, QR, IRN)
try:  # pragma: no cover
    from .crypto.firs_signing import FIRSSigner as ZutaxSigner  # type: ignore
except Exception:  # pragma: no cover
    ZutaxSigner = None  # type: ignore

try:  # pragma: no cover
    from .crypto.firs_qrcode import FIRSQRCodeGenerator  # type: ignore
except Exception:  # pragma: no cover
    FIRSQRCodeGenerator = None  # type: ignore

try:  # pragma: no cover
    from .crypto.irn import IRNGenerator  # type: ignore
except Exception:  # pragma: no cover
    IRNGenerator = None  # type: ignore

from .models import (  # noqa: F401
    InvoiceType,
    InvoiceStatus,
    PaymentMethod,
    StateCode,
    UnitOfMeasure,
)

from .__version__ import __version__  # noqa: F401


__all__ = [
    # Core renamed classes
    "ZutaxClient",
    "ZutaxConfig",
    "ZutaxSigner",
    "FIRSQRCodeGenerator",
    "IRNGenerator",
    # Models / builders
    "Invoice",
    "Party",
    "Address",
    "LineItem",
    "InvoiceBuilder",
    "LineItemBuilder",
    # Managers
    "HSNManager",
    "HSNCode",
    "TaxManager",
    "SimpleTaxCalculation",
    "SimpleTaxBreakdown",
    "PaymentDetails",
    # API
    "ZutaxAPIClient",
    "zutax_api_client",
    "ZutaxAPIError",
    "ZutaxAPIResponse",
    "InvoiceAPI",
    "FIRSValidationResponse",
    "InvoiceSubmissionResult",
    "ResourceAPI",
    # Enums
    "InvoiceType",
    "InvoiceStatus",
    "PaymentMethod",
    "StateCode",
    "UnitOfMeasure",
    # Processing
    "InvoiceProcessor",
    "ProcessingResult",
]
