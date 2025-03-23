"""
API Models

This module contains Pydantic models for the API.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    """Request model for prompt enhancement and processing."""
    prompt: str
    provider: str = "openai"
    model: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    bypass_enhancement: bool = False

class FeedbackRequest(BaseModel):
    """Request model for providing feedback on prompt enhancement."""
    enhancement_index: int
    rating: int  # 1-5 scale

class PromptResponse(BaseModel):
    """Response model for LLM-generated content."""
    response: str
    enhancement_index: Optional[int] = None
