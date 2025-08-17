"""FIRS API client with retry logic and authentication."""

import time
from typing import Any, Dict, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..config.settings import get_config


class APIResponse:
    """Standardized API response wrapper."""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, 
                 message: str = None, status_code: int = None):
        self.success = success
        self.data = data
        self.error = error
        self.message = message
        self.status_code = status_code


class APIError(Exception):
    """Custom API error with status code and response details."""
    
    def __init__(self, message: str, status_code: int = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class FIRSAPIClient:
    """FIRS API client with singleton pattern, retry logic and authentication."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.config = get_config()
        self.session = requests.Session()
        self.retry_count = {}
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay / 1000,  # Convert to seconds
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.config.api_key,
            'x-api-secret': self.config.api_secret
        })
        
        self._initialized = True
    
    def _log_request(self, method: str, url: str) -> None:
        """Log API request."""
        print(f"[API Request] {method.upper()} {url}")
    
    def _log_response(self, status_code: int, url: str) -> None:
        """Log API response."""
        print(f"[API Response] {status_code} {url}")
    
    def _log_error(self, status_code: int, url: str, message: str) -> None:
        """Log API error."""
        print(f"[API Error] {status_code} {url}: {message}")
    
    def _handle_error(self, response: requests.Response) -> APIResponse:
        """Handle HTTP errors and convert to APIResponse."""
        try:
            error_data = response.json()
            message = error_data.get('message', 'An error occurred')
        except:
            message = f"HTTP {response.status_code} error"
        
        self._log_error(response.status_code, response.url, message)
        
        return APIResponse(
            success=False,
            error=f"HTTP {response.status_code}",
            message=message,
            status_code=response.status_code
        )
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, **kwargs) -> APIResponse:
        """Make GET request."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self._log_request('GET', url)
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.config.timeout / 1000,  # Convert to seconds
                **kwargs
            )
            
            self._log_response(response.status_code, url)
            
            if response.status_code >= 400:
                return self._handle_error(response)
            
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Request failed"
            )
    
    def post(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> APIResponse:
        """Make POST request."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self._log_request('POST', url)
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.config.timeout / 1000,  # Convert to seconds
                **kwargs
            )
            
            self._log_response(response.status_code, url)
            
            if response.status_code >= 400:
                return self._handle_error(response)
            
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Request failed"
            )
    
    def put(self, endpoint: str, data: Any = None, json: Any = None, **kwargs) -> APIResponse:
        """Make PUT request."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self._log_request('PUT', url)
        
        try:
            response = self.session.put(
                url,
                data=data,
                json=json,
                timeout=self.config.timeout / 1000,  # Convert to seconds
                **kwargs
            )
            
            self._log_response(response.status_code, url)
            
            if response.status_code >= 400:
                return self._handle_error(response)
            
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Request failed"
            )
    
    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        """Make DELETE request."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self._log_request('DELETE', url)
        
        try:
            response = self.session.delete(
                url,
                timeout=self.config.timeout / 1000,  # Convert to seconds
                **kwargs
            )
            
            self._log_response(response.status_code, url)
            
            if response.status_code >= 400:
                return self._handle_error(response)
            
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )
            
        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Request failed"
            )
    
    def update_headers(self, headers: Dict[str, str]) -> None:
        """Update session headers."""
        self.session.headers.update(headers)
    
    def set_auth_credentials(self, api_key: str, api_secret: str) -> None:
        """Update API authentication credentials."""
        self.update_headers({
            'x-api-key': api_key,
            'x-api-secret': api_secret
        })


# Global singleton instance
api_client = FIRSAPIClient()