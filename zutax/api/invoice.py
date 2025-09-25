"""Zutax Invoice API endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .client import api_client
from ..models.invoice import Invoice
from ..schemas.validators_impl import InvoiceValidator  # type: ignore


class FIRSValidationResponse(BaseModel):
    """FIRS validation response model."""

    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    irn: Optional[str] = None
    qr_code: Optional[str] = None


class InvoiceSubmissionResult(BaseModel):
    """Invoice submission result model."""

    success: bool
    irn: Optional[str] = None
    qr_code: Optional[str] = None
    errors: List[str] = []
    warnings: List[str] = []
    submission_id: Optional[str] = None
    status: Optional[str] = None


class InvoiceAPI:
    """Invoice API operations."""

    @staticmethod
    def validate_local(invoice: Invoice) -> Dict[str, Any]:
        """Validate invoice locally using Pydantic schemas."""
        try:
            # Use InvoiceValidator for local validation
            validation_result = InvoiceValidator.validate_invoice(invoice)

            return {
                "valid": validation_result["valid"],
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
            }
        except Exception as e:  # pragma: no cover - defensive
            return {"valid": False, "errors": [str(e)], "warnings": []}

    @staticmethod
    async def validate_remote(invoice: Invoice) -> FIRSValidationResponse:
        """Validate invoice with FIRS API."""
        response = api_client.post(  # type: ignore[attr-defined]
            "/api/v1/invoice/validate", json=invoice.model_dump()
        )

        if not response.success:  # type: ignore[union-attr]
            return FIRSValidationResponse(
                valid=False,
                errors=[
                    getattr(response, "error", None) or "Validation failed"
                ],
            )

        data = getattr(response, "data", None) or {}
        return FIRSValidationResponse(
            valid=data.get("valid", False),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            irn=data.get("irn"),
            qr_code=data.get("qr_code"),
        )

    @staticmethod
    async def submit_invoice(invoice: Invoice) -> InvoiceSubmissionResult:
        """Submit invoice to FIRS for processing."""
        # First validate locally
        local_validation = InvoiceAPI.validate_local(invoice)
        if not local_validation["valid"]:
            return InvoiceSubmissionResult(
                success=False, errors=local_validation["errors"]
            )

        # Submit to FIRS
        response = api_client.post(  # type: ignore[attr-defined]
            "/api/v1/invoice/submit", json=invoice.model_dump(mode="json")
        )

        if not response.success:  # type: ignore[union-attr]
            return InvoiceSubmissionResult(
                success=False,
                errors=[
                    getattr(response, "error", None) or "Submission failed"
                ],
            )

        data = getattr(response, "data", None) or {}
        return InvoiceSubmissionResult(
            success=data.get("success", False),
            irn=data.get("irn"),
            qr_code=data.get("qr_code"),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            submission_id=data.get("submission_id"),
            status=data.get("status"),
        )

    @staticmethod
    async def get_invoice_status(irn: str) -> Dict[str, Any]:
        """Get invoice status by IRN."""
        response = api_client.get(  # type: ignore[attr-defined]
            f"/api/v1/invoice/status/{irn}"
        )

        if not response.success:  # type: ignore[union-attr]
            return {
                "success": False,
                "error": getattr(response, "error", None)
                or "Failed to get status",
            }

        return {"success": True, "data": getattr(response, "data", None)}

    @staticmethod
    async def cancel_invoice(irn: str, reason: str) -> Dict[str, Any]:
        """Cancel an invoice."""
        response = api_client.post(  # type: ignore[attr-defined]
            f"/api/v1/invoice/cancel/{irn}", json={"reason": reason}
        )

        if not response.success:  # type: ignore[union-attr]
            return {
                "success": False,
                "error": getattr(response, "error", None)
                or "Failed to cancel invoice",
            }

        return {"success": True, "data": getattr(response, "data", None)}

    @staticmethod
    async def batch_validate(
        invoices: List[Invoice],
    ) -> List[FIRSValidationResponse]:
        """Batch validate multiple invoices."""
        invoice_data = [invoice.model_dump() for invoice in invoices]
        response = api_client.post(  # type: ignore[attr-defined]
            "/api/v1/invoice/batch-validate", json={"invoices": invoice_data}
        )

        if not response.success:  # type: ignore[union-attr]
            # Return failed validation for all invoices
            return [
                FIRSValidationResponse(
                    valid=False,
                    errors=[
                        getattr(response, "error", None)
                        or "Batch validation failed"
                    ],
                )
                for _ in invoices
            ]

        data = getattr(response, "data", {})
        results = data.get("results", [])
        return [
            FIRSValidationResponse(
                valid=result.get("valid", False),
                errors=result.get("errors", []),
                warnings=result.get("warnings", []),
                irn=result.get("irn"),
                qr_code=result.get("qr_code"),
            )
            for result in results
        ]
