"""
SQLAlchemy ORM models for chat messages.
Stores user and model messages linked to anonymous sessions.
"""

from sqlalchemy import Column, DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.session import Base


class Message(Base):
    """
    Chat message model for storing conversation history.
    
    Stores both user and model (AI) messages linked to sessions.
    Immutable after creation - no update operations supported.
    """
    
    __tablename__ = "messages"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique message identifier (UUID4)"
    )
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Reference to session this message belongs to"
    )
    
    role = Column(
        String(10),
        nullable=False,
        doc="Message role: 'user' for user messages, 'model' for AI responses"
    )
    
    content = Column(
        Text,
        nullable=False,
        doc="Message text content"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Message creation timestamp (UTC)"
    )
    
    # Index for efficient retrieval of session message history
    __table_args__ = (
        None,  # Placeholder for potential constraints
    )
    
    def __repr__(self) -> str:
        role_char = "U" if self.role == "user" else "M"
        return f"<Message(id={self.id}, session={self.session_id}, role={role_char}, created={self.created_at})>"
