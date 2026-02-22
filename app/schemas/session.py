"""
Pydantic schemas for session request/response validation.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class SessionCreate(BaseModel):
    """
    Schema for session creation requests.
    Allows empty body for simple session creation.
    """
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "description": "Empty request body creates a new anonymous session"
        }


class SessionResponse(BaseModel):
    """
    Schema for session response in API responses.
    Contains session identifier and creation metadata.
    """
    
    session_id: UUID = Field(
        ...,
        description="Unique session identifier (UUID4)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    
    created_at: datetime = Field(
        ...,
        description="Session creation timestamp in ISO 8601 format",
        example="2026-02-21T13:30:45.123456"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "description": "Anonymous user session response",
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-21T13:30:45.123456"
            }
        }
    
    @classmethod
    def from_model(cls, session):
        """
        Create SessionResponse from database model.
        
        Args:
            session: SQLAlchemy Session model instance
            
        Returns:
            SessionResponse with session data
        """
        return cls(
            session_id=session.id,
            created_at=session.created_at
        )
