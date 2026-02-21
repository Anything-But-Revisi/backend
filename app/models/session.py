"""
SQLAlchemy ORM models for SafeSpace sessions.
Defines Session model for anonymous user sessions.
"""

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Session(Base):
    """
    Anonymous user session model.
    
    Stores minimal session metadata with UUID-based identifiers.
    No personally identifiable information is stored.
    """
    
    __tablename__ = "sessions"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique session identifier (UUID4)"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Session creation timestamp (UTC)"
    )
    
    # Relationships
    reports = relationship(
        "Report",
        back_populates="session",
        cascade="all, delete-orphan",
        doc="Reports (incident forms) associated with this session"
    )
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, created_at={self.created_at})>"
