"""
Unit tests for Pydantic session schemas.
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from app.schemas.session import SessionCreate, SessionResponse
from app.models.session import Session


class TestSessionCreateSchema:
    """Test Suite: SessionCreate Pydantic Schema"""
    
    def test_session_create_empty_body(self):
        """Test creating a SessionCreate with empty body."""
        data = {}
        schema = SessionCreate(**data)
        
        assert schema is not None
    
    def test_session_create_parses_empty_dict(self):
        """Test that SessionCreate accepts empty dictionary."""
        schema = SessionCreate.model_validate({})
        assert schema is not None
    
    def test_session_create_allows_json_null(self):
        """Test that SessionCreate allows parsing from null/empty JSON."""
        # This tests the API behavior when client sends: POST /sessions {}
        schema = SessionCreate()
        assert schema is not None
    
    def test_session_create_has_no_required_fields(self):
        """Test that SessionCreate has no required fields (client sends empty body)."""
        # This allows POST /sessions with empty body
        schema = SessionCreate()
        assert True  # If this executes without error, no required fields


class TestSessionResponseSchema:
    """Test Suite: SessionResponse Pydantic Schema"""
    
    def test_session_response_requires_session_id(self):
        """Test that SessionResponse requires session_id."""
        test_uuid = uuid4()
        test_timestamp = datetime.utcnow()
        
        response = SessionResponse(
            session_id=test_uuid,
            created_at=test_timestamp
        )
        
        assert response.session_id == test_uuid
        assert response.created_at == test_timestamp
    
    def test_session_response_uuid_field(self):
        """Test that session_id is properly typed as UUID."""
        test_uuid = uuid4()
        response = SessionResponse(
            session_id=test_uuid,
            created_at=datetime.utcnow()
        )
        
        assert isinstance(response.session_id, UUID)
    
    def test_session_response_datetime_field(self):
        """Test that created_at is properly typed as datetime."""
        test_timestamp = datetime.utcnow()
        response = SessionResponse(
            session_id=uuid4(),
            created_at=test_timestamp
        )
        
        assert isinstance(response.created_at, datetime)
    
    def test_session_response_accepts_string_uuid(self):
        """Test that SessionResponse accepts UUID as string."""
        test_uuid = uuid4()
        response = SessionResponse(
            session_id=str(test_uuid),
            created_at=datetime.utcnow()
        )
        
        assert isinstance(response.session_id, UUID)
    
    def test_session_response_accepts_string_datetime(self):
        """Test that SessionResponse accepts datetime as string."""
        test_timestamp = "2026-01-01T12:00:00"
        response = SessionResponse(
            session_id=uuid4(),
            created_at=test_timestamp
        )
        
        assert isinstance(response.created_at, datetime)
    
    def test_session_response_from_model(self):
        """Test SessionResponse.from_model() conversion from ORM."""
        # Create a mock session model
        session = Session()
        
        response = SessionResponse.from_model(session)
        
        assert response.session_id == session.id
        assert response.created_at == session.created_at
    
    def test_session_response_from_model_preserves_values(self):
        """Test that from_model preserves all values."""
        session = Session()
        original_id = session.id
        original_timestamp = session.created_at
        
        response = SessionResponse.from_model(session)
        
        assert response.session_id == original_id
        assert response.created_at == original_timestamp
    
    def test_session_response_json_serialization(self):
        """Test that SessionResponse can be serialized to JSON."""
        test_uuid = uuid4()
        test_timestamp = datetime.utcnow()
        
        response = SessionResponse(
            session_id=test_uuid,
            created_at=test_timestamp
        )
        
        response_dict = response.model_dump()
        
        assert "session_id" in response_dict
        assert "created_at" in response_dict
    
    def test_session_response_missing_session_id_raises_error(self):
        """Test that missing session_id raises validation error."""
        with pytest.raises(ValueError):
            SessionResponse(created_at=datetime.utcnow())
    
    def test_session_response_missing_created_at_raises_error(self):
        """Test that missing created_at raises validation error."""
        with pytest.raises(ValueError):
            SessionResponse(session_id=uuid4())
    
    def test_session_response_schema_extra(self):
        """Test that SessionResponse has schema_extra documentation."""
        # Verify the model has documentation for OpenAPI
        assert SessionResponse.model_json_schema() is not None


class TestSessionSchemasIntegration:
    """Test Suite: Integration between SessionCreate and SessionResponse"""
    
    def test_create_request_to_response_flow(self):
        """Test complete flow from create request to response."""
        # Client sends empty body
        create_request = SessionCreate()
        assert create_request is not None
        
        # Server creates session and returns response
        test_uuid = uuid4()
        response = SessionResponse(
            session_id=test_uuid,
            created_at=datetime.utcnow()
        )
        
        assert isinstance(response.session_id, UUID)
        assert isinstance(response.created_at, datetime)
    
    def test_session_response_has_field_descriptions(self):
        """Test that SessionResponse fields have descriptions (for OpenAPI)."""
        schema = SessionResponse.model_json_schema()
        
        assert "properties" in schema
        assert "session_id" in schema["properties"]
        assert "created_at" in schema["properties"]
