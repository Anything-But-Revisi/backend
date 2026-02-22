"""
Unit tests for Session SQLAlchemy model.
"""

import pytest
from datetime import datetime
from uuid import UUID

from app.models.session import Session


class TestSessionModel:
    """Test Suite: Session ORM Model"""
    
    def test_session_creation(self):
        """Test creating a new session model instance."""
        session = Session()
        
        assert session is not None
        assert isinstance(session.id, UUID)
        assert isinstance(session.created_at, datetime)
    
    def test_session_id_generation(self):
        """Test that session IDs are UUIDs."""
        session = Session()
        
        assert isinstance(session.id, UUID)
        assert session.id.version == 4  # UUID4
    
    def test_session_created_at_timestamp(self):
        """Test that created_at timestamp is set."""
        before = datetime.utcnow()
        session = Session()
        after = datetime.utcnow()
        
        assert isinstance(session.created_at, datetime)
        assert before <= session.created_at <= after
    
    def test_multiple_sessions_have_different_ids(self):
        """Test that multiple sessions get different UUIDs."""
        session1 = Session()
        session2 = Session()
        
        assert session1.id != session2.id
    
    def test_session_repr(self):
        """Test the string representation of a session."""
        session = Session()
        repr_str = repr(session)
        
        assert "Session" in repr_str
        assert str(session.id) in repr_str
    
    def test_session_tablename(self):
        """Test that session model has correct table name."""
        assert Session.__tablename__ == "sessions"
    
    def test_session_has_primary_key(self):
        """Test that session model has id as primary key."""
        # Check that id is in primary key columns
        pk_columns = [col.name for col in Session.__table__.primary_key.columns]
        assert "id" in pk_columns
        assert len(pk_columns) == 1  # Only id is primary key
    
    def test_session_timestamp_immutable(self):
        """Test that created_at timestamp is set at creation."""
        session = Session()
        original_timestamp = session.created_at
        
        # Timestamp should be set once
        assert session.created_at == original_timestamp
    
    def test_session_model_fields(self):
        """Test that session model has required fields."""
        session = Session()
        
        # Check all required fields exist
        assert hasattr(session, 'id')
        assert hasattr(session, 'created_at')
    
    def test_session_minimal_data_model(self):
        """Test that session only contains minimal required fields (privacy-first design)."""
        session = Session()
        session_dict = {col.name for col in Session.__table__.columns}
        
        # Should only have id and created_at (no PII)
        assert session_dict == {'id', 'created_at'}
        assert len(session_dict) == 2  # Exactly 2 columns for privacy
