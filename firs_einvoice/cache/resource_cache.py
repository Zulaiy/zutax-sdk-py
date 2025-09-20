"""Resource caching implementation for FIRS API responses."""

import time
import threading
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass
from pydantic import BaseModel

from ..config.settings import get_config


class CacheEntry(BaseModel):
    """Cache entry model."""
    data: Any
    timestamp: float
    ttl: float


class ResourceCache:
    """Thread-safe resource cache for FIRS API responses."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
    # Avoid hard-failing at import time if config/env isn't ready (e.g., tests)
        try:
            self.config = get_config()
            self.default_ttl = getattr(self.config, 'cache_ttl', 300)
        except Exception:
            # Fall back to safe defaults so the cache can still operate
            self.config = None
            self.default_ttl = 300
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        self._lock = threading.RLock()
        self._initialized = True
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        return time.time() - entry.timestamp > entry.ttl
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            print(f"Cache expired for key: {key}")
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        with self._lock:
            self._cleanup_expired()
            
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    self._stats['hits'] += 1
                    print(f"Cache hit for key: {key}")
                    return entry.data
                else:
                    del self._cache[key]
            
            self._stats['misses'] += 1
            print(f"Cache miss for key: {key}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        try:
            with self._lock:
                ttl = ttl or self.default_ttl
                entry = CacheEntry(
                    data=value,
                    timestamp=time.time(),
                    ttl=ttl
                )
                self._cache[key] = entry
                self._stats['sets'] += 1
                print(f"Cache set for key: {key}, TTL: {ttl}s")
                return True
        except Exception as error:
            print(f"Error setting cache for key {key}: {error}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: Optional[float] = None,
    ) -> Any:
        """Get value from cache or set using factory function."""
        # Check if value exists in cache
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Get fresh value
        try:
            fresh_value = await factory()
            self.set(key, fresh_value, ttl)
            return fresh_value
        except Exception as error:
            print(f"Error in factory function for key {key}: {error}")
            raise error
    
    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    return True
                else:
                    del self._cache[key]
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                print(f"Cache deleted for key: {key}")
                return True
            return False
    
    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache."""
        deleted_count = 0
        with self._lock:
            for key in keys:
                if key in self._cache:
                    del self._cache[key]
                    deleted_count += 1
            
            self._stats['deletes'] += deleted_count
            print(f"Cache deleted {deleted_count} keys")
            return deleted_count
    
    def clear(self) -> None:
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
            print("All cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            self._cleanup_expired()
            hit_rate = 0
            total_requests = self._stats['hits'] + self._stats['misses']
            if total_requests > 0:
                hit_rate = (self._stats['hits'] / total_requests) * 100
            
            return {
                'keys': len(self._cache),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'size': len(str(self._cache))  # Approximate size
            }
    
    def get_keys(self) -> List[str]:
        """Get all keys in cache."""
        with self._lock:
            self._cleanup_expired()
            return list(self._cache.keys())
    
    def update_ttl(self, key: str, ttl: float) -> bool:
        """Update TTL for a key."""
        with self._lock:
            if key in self._cache:
                self._cache[key].ttl = ttl
                self._cache[key].timestamp = time.time()  # Reset timestamp
                return True
            return False
    
    def get_ttl(self, key: str) -> Optional[float]:
        """Get remaining TTL for a key."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                remaining = entry.ttl - (time.time() - entry.timestamp)
                return max(0, remaining)
            return None
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Batch get multiple keys."""
        result = {}
        with self._lock:
            self._cleanup_expired()
            for key in keys:
                if key in self._cache:
                    entry = self._cache[key]
                    if not self._is_expired(entry):
                        result[key] = entry.data
                        self._stats['hits'] += 1
                    else:
                        del self._cache[key]
                        self._stats['misses'] += 1
                else:
                    self._stats['misses'] += 1
        
        return result
    
    def set_many(self, entries: List[Dict[str, Any]]) -> bool:
        """Batch set multiple key-value pairs."""
        try:
            with self._lock:
                for entry in entries:
                    key = entry['key']
                    value = entry['value']
                    ttl = entry.get('ttl', self.default_ttl)
                    
                    cache_entry = CacheEntry(
                        data=value,
                        timestamp=time.time(),
                        ttl=ttl
                    )
                    self._cache[key] = cache_entry
                    self._stats['sets'] += 1
                
                return True
        except Exception as error:
            print(f"Error setting multiple cache entries: {error}")
            return False
    
    @staticmethod
    def create_key(*parts: str) -> str:
        """Create cache key from multiple parts."""
        return ':'.join(parts)
    
    # Cache key prefixes for different resource types
    KEY_PREFIXES = {
        'VAT_EXEMPTIONS': 'vat_exemptions',
        'PRODUCT_CODES': 'product_codes',
        'SERVICE_CODES': 'service_codes',
        'STATES': 'states',
        'LGAS': 'lgas',
        'INVOICE_TYPES': 'invoice_types',
        'TAX_CATEGORIES': 'tax_categories',
        'VALIDATED_INVOICE': 'validated_invoice',
    }


# Global singleton instance
resource_cache = ResourceCache()
