"""FIRS Resources API endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from .client import api_client


class VATExemption(BaseModel):
    """VAT exemption model."""
    code: str
    description: str
    category: str


class ProductCode(BaseModel):
    """Product code model."""
    code: str
    description: str
    hsn_code: Optional[str] = None


class ServiceCode(BaseModel):
    """Service code model."""
    code: str
    description: str
    category: str


class State(BaseModel):
    """Nigerian state model."""
    code: str
    name: str


class LGA(BaseModel):
    """Local Government Area model."""
    code: str
    name: str
    state_code: str


class InvoiceType(BaseModel):
    """Invoice type model."""
    code: str
    description: str
    category: str


class TaxCategory(BaseModel):
    """Tax category model."""
    code: str
    description: str
    rate: float


class ResourceAPI:
    """FIRS Resources API operations."""
    
    @staticmethod
    async def get_vat_exemptions() -> List[VATExemption]:
        """Get VAT exemptions list."""
        response = api_client.get('/api/v1/invoice/resources/vat-exemptions')
        
        if not response.success:
            print(f"Failed to get VAT exemptions: {response.error}")
            return []
        
        data = response.data or []
        return [VATExemption(**item) for item in data]
    
    @staticmethod
    async def get_product_codes() -> List[ProductCode]:
        """Get product codes list."""
        response = api_client.get('/api/v1/invoice/resources/product-codes')
        
        if not response.success:
            print(f"Failed to get product codes: {response.error}")
            return []
        
        data = response.data or []
        return [ProductCode(**item) for item in data]
    
    @staticmethod
    async def get_service_codes() -> List[ServiceCode]:
        """Get service codes list."""
        response = api_client.get('/api/v1/invoice/resources/service-codes')
        
        if not response.success:
            print(f"Failed to get service codes: {response.error}")
            return []
        
        data = response.data or []
        return [ServiceCode(**item) for item in data]
    
    @staticmethod
    async def get_states() -> List[State]:
        """Get Nigerian states list."""
        response = api_client.get('/api/v1/invoice/resources/states')
        
        if not response.success:
            print(f"Failed to get states: {response.error}")
            return []
        
        data = response.data or []
        return [State(**item) for item in data]
    
    @staticmethod
    async def get_lgas(state_code: Optional[str] = None) -> List[LGA]:
        """Get Local Government Areas list."""
        endpoint = '/api/v1/invoice/resources/lgas'
        if state_code:
            endpoint += f'?state_code={state_code}'
        
        response = api_client.get(endpoint)
        
        if not response.success:
            print(f"Failed to get LGAs: {response.error}")
            return []
        
        data = response.data or []
        return [LGA(**item) for item in data]
    
    @staticmethod
    async def get_invoice_types() -> List[InvoiceType]:
        """Get invoice types list."""
        response = api_client.get('/api/v1/invoice/resources/invoice-types')
        
        if not response.success:
            print(f"Failed to get invoice types: {response.error}")
            return []
        
        data = response.data or []
        return [InvoiceType(**item) for item in data]
    
    @staticmethod
    async def get_tax_categories() -> List[TaxCategory]:
        """Get tax categories list."""
        response = api_client.get('/api/v1/invoice/resources/tax-categories')
        
        if not response.success:
            print(f"Failed to get tax categories: {response.error}")
            return []
        
        data = response.data or []
        return [TaxCategory(**item) for item in data]
    
    @staticmethod
    async def preload_resources() -> Dict[str, Any]:
        """Preload all essential resources."""
        from ..cache.resource_cache import resource_cache
        
        results = {}
        
        # Load all resources in parallel
        try:
            results['vat_exemptions'] = await ResourceAPI.get_vat_exemptions()
            results['product_codes'] = await ResourceAPI.get_product_codes()
            results['service_codes'] = await ResourceAPI.get_service_codes()
            results['states'] = await ResourceAPI.get_states()
            results['lgas'] = await ResourceAPI.get_lgas()
            results['invoice_types'] = await ResourceAPI.get_invoice_types()
            results['tax_categories'] = await ResourceAPI.get_tax_categories()
            
            # Cache the results
            for key, value in results.items():
                resource_cache.set(key, value, ttl=3600)  # Cache for 1 hour
            
            print("✓ All resources preloaded successfully")
            
        except Exception as e:
            print(f"Failed to preload resources: {e}")
        
        return results
    
    @staticmethod
    async def refresh_all_resources() -> Dict[str, Any]:
        """Refresh all cached resources."""
        from ..cache.resource_cache import resource_cache
        
        # Clear cache first
        resource_cache.clear()
        
        # Reload all resources
        return await ResourceAPI.preload_resources()