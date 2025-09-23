"""Base Pydantic model configuration for Zutax (formerly FIRS E-Invoice)."""

from pydantic import BaseModel, ConfigDict
from typing import Any, Dict


class FIRSBaseModel(BaseModel):
    """Base model with SDK-specific configuration for all Pydantic models."""

    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        str_min_length=0,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"example": None},
    )

    def model_dump_json(self, **kwargs) -> str:
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        data = self.model_dump(by_alias=True, exclude_none=True)
        import json
        return json.dumps(data, indent=kwargs.get("indent", 2), default=str)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        data = super().model_dump(**kwargs)
        return self._convert_enums_to_values(data)

    def _convert_enums_to_values(self, obj):
        from enum import Enum
        if isinstance(obj, dict):
            return {
                k: self._convert_enums_to_values(v)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [self._convert_enums_to_values(item) for item in obj]
        if isinstance(obj, Enum):
            return obj.value
        return obj


class StrictBaseModel(FIRSBaseModel):
    """Strict base model with additional validation constraints."""

    _parent_config = FIRSBaseModel.model_config.copy()
    _parent_config.update({
        "extra": "forbid",
        "str_min_length": 1,
    })

    model_config = ConfigDict(**_parent_config)
