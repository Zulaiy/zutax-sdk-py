"""Zutax API client with retry logic and authentication (native)."""

from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import get_config


class APIResponse:
    """Standardized API response wrapper."""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        self.success = success
        self.data = data
        self.error = error
        self.message = message
        self.status_code = status_code


class APIError(Exception):
    """Custom API error with status code and response details."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ZutaxAPIClient:
    """API client with singleton pattern, retry logic and authentication."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self.config = get_config()
        self.session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay / 1000.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers; ZutaxConfig stores api_key/secret as SecretStr
        def _secret(v: Any) -> str:
            return (
                v.get_secret_value()
                if hasattr(v, "get_secret_value")
                else str(v)
            )

        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": _secret(self.config.api_key),
                "x-api-secret": _secret(self.config.api_secret),
            }
        )

        self._initialized = True

    def _full_url(self, endpoint: str) -> str:
        return f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _handle_error(self, response: requests.Response) -> APIResponse:
        try:
            error_data = response.json()
            message = error_data.get("message", f"HTTP {response.status_code}")
        except Exception:
            message = f"HTTP {response.status_code} error"
        return APIResponse(
            success=False,
            error=f"HTTP {response.status_code}",
            message=message,
            status_code=response.status_code,
        )

    def update_headers(self, headers: Dict[str, str]) -> None:
        self.session.headers.update(headers)

    def set_auth_credentials(self, api_key: str, api_secret: str) -> None:
        self.update_headers({"x-api-key": api_key, "x-api-secret": api_secret})

    # HTTP methods
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> APIResponse:
        url = self._full_url(endpoint)
        try:
            response = self.session.get(
                url, params=params, timeout=self.config.timeout, **kwargs
            )
            if response.status_code >= 400:
                return self._handle_error(response)
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            return APIResponse(
                success=False, error=str(e), message="Request failed"
            )

    def post(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        **kwargs,
    ) -> APIResponse:
        url = self._full_url(endpoint)
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.config.timeout,
                **kwargs,
            )
            if response.status_code >= 400:
                return self._handle_error(response)
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            return APIResponse(
                success=False, error=str(e), message="Request failed"
            )

    def put(
        self,
        endpoint: str,
        data: Any = None,
        json: Any = None,
        **kwargs,
    ) -> APIResponse:
        url = self._full_url(endpoint)
        try:
            response = self.session.put(
                url,
                data=data,
                json=json,
                timeout=self.config.timeout,
                **kwargs,
            )
            if response.status_code >= 400:
                return self._handle_error(response)
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            return APIResponse(
                success=False, error=str(e), message="Request failed"
            )

    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        url = self._full_url(endpoint)
        try:
            response = self.session.delete(
                url, timeout=self.config.timeout, **kwargs
            )
            if response.status_code >= 400:
                return self._handle_error(response)
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code,
            )
        except requests.exceptions.RequestException as e:  # pragma: no cover
            return APIResponse(
                success=False, error=str(e), message="Request failed"
            )


# Global singleton instance
try:
    api_client = ZutaxAPIClient()
except Exception:  # pragma: no cover
    api_client = None  # type: ignore


__all__ = ["ZutaxAPIClient", "APIResponse", "APIError", "api_client"]
