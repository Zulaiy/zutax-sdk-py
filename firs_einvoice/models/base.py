"""Base Pydantic model configuration for FIRS E-Invoice."""

from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, Optional


class FIRSBaseModel(BaseModel):
    """Base model with FIRS-specific configuration for all Pydantic models."""

    model_config = ConfigDict(
        # Validation settings
        validate_assignment=True,  # Validate on attribute assignment
        validate_default=True,  # Validate default values
        use_enum_values=True,  # Use enum values instead of enum instances
        
        # String handling
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=0,  # Allow empty strings by default
        
        # Field population
        populate_by_name=True,  # Allow population by field name
        from_attributes=True,  # Allow creating from object attributes
        
        # Type settings
        arbitrary_types_allowed=True,  # Allow arbitrary types
        
        # JSON serialization
        json_encoders={
            Decimal: lambda v: str(v),  # Convert Decimal to string
            datetime: lambda v: v.isoformat(),  # ISO format for datetime
        },
        
        # Schema generation
        json_schema_extra={
            "example": None  # Can be overridden in child classes
        }
    )

    def model_dump_json(self, **kwargs) -> str:
        """Override to ensure proper JSON serialization."""
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('exclude_none', True)
        # First dump to dict to handle enums properly
        data = self.model_dump(by_alias=True, exclude_none=True)
        import json
        return json.dumps(data, indent=kwargs.get('indent', 2), default=str)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override to ensure proper dictionary conversion."""
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('exclude_none', True)
        data = super().model_dump(**kwargs)
        # Convert any enum values to strings
        return self._convert_enums_to_values(data)
    
    def _convert_enums_to_values(self, obj):
        """Recursively convert enum objects to their values."""
        from enum import Enum
        if isinstance(obj, dict):
            return {k: self._convert_enums_to_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_enums_to_values(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj

    @classmethod
    def model_validate_json(cls, json_data: str, **kwargs):
        """Validate JSON string and create model instance."""
        return super().model_validate_json(json_data, **kwargs)


class StrictBaseModel(FIRSBaseModel):
    """Strict base model with additional validation constraints."""

    # Create a copy of parent config and update it
    _parent_config = FIRSBaseModel.model_config.copy()
    _parent_config.update({
        'extra': 'forbid',  # Forbid extra fields
        'str_min_length': 1,  # Require non-empty strings (overrides parent's 0)
    })
    
    model_config = ConfigDict(**_parent_config)