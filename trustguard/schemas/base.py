"""
Base schema classes for trustguard.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict


class BaseResponse(BaseModel):
    """
    Base class for all response schemas.
    """
    model_config = ConfigDict(
        extra="forbid",  # Don't allow extra fields
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
    
    def to_json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)
