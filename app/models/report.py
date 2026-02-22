"""
Migration: Add reports table for sexual violence complaint form generation.

This migration creates a reports table to store structured incident data
and generated complaint form narratives using Gemini LLM.
"""

from sqlalchemy import Column, DateTime, String, Text, ForeignKey, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.session import Base


class Report(Base):
    """
    Sexual violence incident report model.
    
    Stores structured incident information and generated complaint form narratives.
    Reports are session-scoped and cascade-deleted when parent session is deleted.
    """
    
    __tablename__ = "reports"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique report identifier (UUID4)"
    )
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to parent session (cascade delete)"
    )
    
    location = Column(
        String(50),
        nullable=False,
        doc="Location of incident (public space, online, kampus, sekolah, workplace)"
    )
    
    perpetrator = Column(
        String(50),
        nullable=False,
        doc="Type of perpetrator (supervisor, colleague, lecturer, client, stranger)"
    )
    
    description = Column(
        String(100),
        nullable=False,
        doc="Type of incident (inappropriate comments, unwanted physical touch, repeated pressure, threat or coercion, digital harassment)"
    )
    
    evidence = Column(
        String(50),
        nullable=False,
        doc="Type of evidence (messages, emails, witness, none)"
    )
    
    user_goal = Column(
        String(100),
        nullable=False,
        doc="User's goal (understand the risk, document safely, consider reporting, explore options)"
    )
    
    generated_document = Column(
        Text,
        nullable=True,
        doc="Generated complaint form narrative in Indonesian (nullable if Gemini generation fails)"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Report creation timestamp (UTC)"
    )
    
    # Relationships
    session = relationship(
        "Session",
        back_populates="reports",
        doc="Parent session for this report"
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, session={self.session_id}, location={self.location}, created={self.created_at})>"
