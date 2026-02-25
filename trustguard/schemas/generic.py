"""
Generic schema suitable for most LLM outputs.
"""

from pydantic import Field, field_validator
from typing import Optional
from trustguard.schemas.base import BaseResponse


class GenericResponse(BaseResponse):
    """
    A generic schema suitable for most LLM outputs.
    
    Attributes:
        content: The main response content (required)
        sentiment: Sentiment of the response (positive/neutral/negative) (required)
        tone: Tone of the response (required)
        is_helpful: Whether the response is helpful (required)
        confidence: Confidence score (0-1) (optional)
    """
    
    content: str = Field(
        description="The main response content.",
        min_length=1,
        max_length=10000,
    )
    
    sentiment: str = Field(
        description="Sentiment of the response (positive/neutral/negative).",
        pattern="^(positive|neutral|negative)$"
    )
    
    tone: str = Field(
        description="The tone of the response.",
        min_length=1,
    )
    
    is_helpful: bool = Field(
        description="Whether the response is helpful.",
    )
    
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score (0-1).",
        ge=0.0,
        le=1.0,
    )
    
    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v):
        """Validate that tone is not empty."""
        if not v or not v.strip():
            raise ValueError('tone cannot be empty')
        return v.strip()
