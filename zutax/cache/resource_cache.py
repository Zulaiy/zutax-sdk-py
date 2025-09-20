"""Resource caching implementation for API responses (Zutax)."""

import time
import threading
from typing import Any, Dict, List, Optional, Callable, Awaitable
from pydantic import BaseModel

from ..config.settings import get_config


class CacheEntry(BaseModel):
    data: Any
    timestamp: float
    ttl: float


class ResourceCache:
    """Thread-safe resource cache for API responses."""

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

        try:
            self.config = get_config()
            self.default_ttl = getattr(self.config, "cache_ttl", 300)
        except Exception:  # pragma: no cover
            self.config = None
            self.default_ttl = 300
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}
        self._lock = threading.RLock()
        self._initialized = True

    def _is_expired(self, entry: CacheEntry) -> bool:
        return time.time() - entry.timestamp > entry.ttl

    def _cleanup_expired(self) -> None:
        current_time = time.time()
        expired_keys = []
        for key, entry in self._cache.items():
            if current_time - entry.timestamp > entry.ttl:
                expired_keys.append(key)
        for key in expired_keys:
            del self._cache[key]

    def get(self, key: str) -> Any:
        with self._lock:
            self._cleanup_expired()
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    self._stats["hits"] += 1
                    return entry.data
                del self._cache[key]
            self._stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        try:
            with self._lock:
                ttl = ttl or self.default_ttl
                entry = CacheEntry(data=value, timestamp=time.time(), ttl=ttl)
                self._cache[key] = entry
                self._stats["sets"] += 1
                return True
        except Exception:
            return False

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
        ttl: Optional[float] = None,
    ) -> Any:
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        fresh_value = await factory()
        self.set(key, fresh_value, ttl)
        return fresh_value

    def has(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    return True
                del self._cache[key]
            return False

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False

    def delete_many(self, keys: List[str]) -> int:
        deleted_count = 0
        with self._lock:
            for key in keys:
                if key in self._cache:
                    del self._cache[key]
                    deleted_count += 1
            self._stats["deletes"] += deleted_count
            return deleted_count

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            self._cleanup_expired()
            hit_rate = 0
            total_requests = self._stats["hits"] + self._stats["misses"]
            if total_requests > 0:
                hit_rate = (self._stats["hits"] / total_requests) * 100
            return {
                "keys": len(self._cache),
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "size": len(str(self._cache)),
            }

    def get_keys(self) -> List[str]:
        with self._lock:
            self._cleanup_expired()
            return list(self._cache.keys())

    def update_ttl(self, key: str, ttl: float) -> bool:
        with self._lock:
            if key in self._cache:
                self._cache[key].ttl = ttl
                self._cache[key].timestamp = time.time()
                return True
            return False

    def get_ttl(self, key: str) -> Optional[float]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                remaining = entry.ttl - (time.time() - entry.timestamp)
                return max(0, remaining)
            return None

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        with self._lock:
            self._cleanup_expired()
            for key in keys:
                if key in self._cache:
                    entry = self._cache[key]
                    if not self._is_expired(entry):
                        result[key] = entry.data
                        self._stats["hits"] += 1
                    else:
                        del self._cache[key]
                        self._stats["misses"] += 1
                else:
                    self._stats["misses"] += 1
        return result

    def set_many(self, entries: List[Dict[str, Any]]) -> bool:
        try:
            with self._lock:
                for entry in entries:
                    key = entry["key"]
                    value = entry["value"]
                    ttl = entry.get("ttl", self.default_ttl)
                    self._cache[key] = CacheEntry(
                        data=value, timestamp=time.time(), ttl=ttl
                    )
                    self._stats["sets"] += 1
                return True
        except Exception:  # pragma: no cover
            return False

    @staticmethod
    def create_key(*parts: str) -> str:
        return ":".join(parts)

    KEY_PREFIXES = {
        "VAT_EXEMPTIONS": "vat_exemptions",
        "PRODUCT_CODES": "product_codes",
        "SERVICE_CODES": "service_codes",
        "STATES": "states",
        "LGAS": "lgas",
        "INVOICE_TYPES": "invoice_types",
        "TAX_CATEGORIES": "tax_categories",
        "VALIDATED_INVOICE": "validated_invoice",
    }


resource_cache = ResourceCache()

__all__ = ["ResourceCache", "CacheEntry", "resource_cache"]
