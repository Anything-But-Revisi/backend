"""
Pydantic schemas for report (incident form) validation and serialization.

Provides request/response schemas with strict Enum validation for
location, perpetrator, description, evidence, and user goals.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Enum definitions with strict validation
class LocationEnum(str, Enum):
    """Incident location options."""
    PUBLIC_SPACE = "public space"
    ONLINE = "online"
    KAMPUS = "kampus"
    SEKOLAH = "sekolah"
    WORKPLACE = "workplace"


class PerpBtratorEnum(str, Enum):
    """Perpetrator type options."""
    SUPERVISOR = "supervisor"
    COLLEAGUE = "colleague"
    LECTURER = "lecturer"
    CLIENT = "client"
    STRANGER = "stranger"


class DescriptionEnum(str, Enum):
    """Type of incident options."""
    INAPPROPRIATE_COMMENTS = "inappropriate comments"
    UNWANTED_PHYSICAL_TOUCH = "unwanted physical touch"
    REPEATED_PRESSURE = "repeated pressure"
    THREAT_OR_COERCION = "threat or coercion"
    DIGITAL_HARASSMENT = "digital harassment"


class EvidenceEnum(str, Enum):
    """Type of evidence options."""
    MESSAGES = "messages"
    EMAILS = "emails"
    WITNESS = "witness"
    NONE = "none"


class UserGoalEnum(str, Enum):
    """User's primary goal options."""
    UNDERSTAND_RISK = "understand the risk"
    DOCUMENT_SAFELY = "document safely"
    CONSIDER_REPORTING = "consider reporting"
    EXPLORE_OPTIONS = "explore options"


class ReportCreate(BaseModel):
    """
    Request schema for creating a new report.
    
    Accepts structured incident information with strict Enum validation.
    All fields are required.
    """
    location: LocationEnum = Field(
        ...,
        description="Location where incident occurred"
    )
    perpetrator: PerpBtratorEnum = Field(
        ...,
        description="Type of perpetrator"
    )
    description: DescriptionEnum = Field(
        ...,
        description="Type/nature of incident"
    )
    evidence: EvidenceEnum = Field(
        ...,
        description="Type of evidence or documentation"
    )
    user_goal: UserGoalEnum = Field(
        ...,
        description="User's primary objective"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True  # Serialize Enum as string values


class ReportResponse(BaseModel):
    """
    Response schema for report retrieval.
    
    Includes all input fields plus system-generated fields
    (id, session_id, generated_document, created_at).
    """
    id: UUID = Field(
        ...,
        description="Unique report identifier"
    )
    session_id: UUID = Field(
        ...,
        description="Parent session identifier"
    )
    location: LocationEnum = Field(
        ...,
        description="Location where incident occurred"
    )
    perpetrator: PerpBtratorEnum = Field(
        ...,
        description="Type of perpetrator"
    )
    description: DescriptionEnum = Field(
        ...,
        description="Type/nature of incident"
    )
    evidence: EvidenceEnum = Field(
        ...,
        description="Type of evidence or documentation"
    )
    user_goal: UserGoalEnum = Field(
        ...,
        description="User's primary objective"
    )
    generated_document: Optional[str] = Field(
        None,
        description="Generated complaint form narrative (nullable if Gemini generation fails)"
    )
    created_at: datetime = Field(
        ...,
        description="Report creation timestamp (UTC)"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Support loading from ORM models
        use_enum_values = True  # Serialize Enum as string values
