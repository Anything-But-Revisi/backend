"""
Integration tests for Session API endpoints.
"""

import pytest
import pytest_asyncio
from uuid import UUID
from datetime import datetime
from httpx import AsyncClient

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models.session import Session, Base
from app.schemas.session import SessionResponse


# In-memory SQLite for testing
@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory test database."""
    # Use SQLite with async support for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    """Create an AsyncClient for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestSessionCreationEndpoint:
    """Test Suite: POST /api/v1/sessions (Create Session)"""
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, client):
        """Test successful session creation."""
        response = await client.post("/api/v1/sessions")
        
        assert response.status_code == 201
        data = response.json()
        
        assert "session_id" in data
        assert "created_at" in data
        assert isinstance(UUID(data["session_id"]), UUID)
    
    @pytest.mark.asyncio
    async def test_create_session_returns_201_status(self, client):
        """Test that session creation returns 201 Created status."""
        response = await client.post("/api/v1/sessions")
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_session_with_empty_body(self, client):
        """Test session creation with empty request body."""
        response = await client.post("/api/v1/sessions", json={})
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
    
    @pytest.mark.asyncio
    async def test_create_session_without_body(self, client):
        """Test session creation without request body."""
        response = await client.post("/api/v1/sessions")
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_created_session_has_uuid_format(self, client):
        """Test that created session ID is a valid UUID."""
        response = await client.post("/api/v1/sessions")
        data = response.json()
        
        session_id = data["session_id"]
        # Should be able to parse as UUID
        parsed_uuid = UUID(session_id)
        assert parsed_uuid.version == 4  # Should be UUID4
    
    @pytest.mark.asyncio
    async def test_created_session_has_timestamp(self, client):
        """Test that created session has a timestamp."""
        before = datetime.utcnow()
        response = await client.post("/api/v1/sessions")
        after = datetime.utcnow()
        
        data = response.json()
        created_at = datetime.fromisoformat(data["created_at"])
        
        # Timestamp should be between before and after
        assert before <= created_at <= after
    
    @pytest.mark.asyncio
    async def test_create_multiple_sessions_different_ids(self, client):
        """Test that multiple sessions get different UUIDs."""
        response1 = await client.post("/api/v1/sessions")
        response2 = await client.post("/api/v1/sessions")
        
        id1 = response1.json()["session_id"]
        id2 = response2.json()["session_id"]
        
        assert id1 != id2
    
    @pytest.mark.asyncio
    async def test_session_response_has_correct_schema(self, client):
        """Test that response matches SessionResponse schema."""
        response = await client.post("/api/v1/sessions")
        data = response.json()
        
        # Should be able to validate against SessionResponse
        session_response = SessionResponse.model_validate(data)
        
        assert isinstance(session_response.session_id, UUID)
        assert isinstance(session_response.created_at, datetime)
    
    @pytest.mark.asyncio
    async def test_create_session_content_type_json(self, client):
        """Test that response content-type is JSON."""
        response = await client.post("/api/v1/sessions")
        
        assert "application/json" in response.headers.get("content-type", "")


class TestSessionDeletionEndpoint:
    """Test Suite: DELETE /api/v1/sessions/{session_id} (Delete Session)"""
    
    @pytest.mark.asyncio
    async def test_delete_session_success(self, client):
        """Test successful session deletion."""
        # Create session
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Delete session
        delete_response = await client.delete(f"/api/v1/sessions/{session_id}")
        
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_session_returns_204_status(self, client):
        """Test that session deletion returns 204 No Content."""
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        delete_response = await client.delete(f"/api/v1/sessions/{session_id}")
        
        assert delete_response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_session_no_content_response(self, client):
        """Test that delete response has no body."""
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        delete_response = await client.delete(f"/api/v1/sessions/{session_id}")
        
        assert delete_response.content == b""
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_session_returns_404(self, client):
        """Test that deleting non-existent session returns 404."""
        fake_uuid = "00000000-0000-4000-8000-000000000000"
        
        response = await client.delete(f"/api/v1/sessions/{fake_uuid}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_session_has_error_detail(self, client):
        """Test that 404 response includes error detail."""
        fake_uuid = "00000000-0000-4000-8000-000000000000"
        
        response = await client.delete(f"/api/v1/sessions/{fake_uuid}")
        data = response.json()
        
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_delete_invalid_uuid_format_returns_422(self, client):
        """Test that invalid UUID format returns 422."""
        response = await client.delete("/api/v1/sessions/invalid-uuid")
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_delete_then_get_returns_404(self, client):
        """Test that deleted session cannot be deleted again."""
        # Create session
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Delete session
        await client.delete(f"/api/v1/sessions/{session_id}")
        
        # Try to delete again - should be 404
        response = await client.delete(f"/api/v1/sessions/{session_id}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_is_permanent(self, client):
        """Test that deletion is permanent (hard delete)."""
        # Create session
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Delete session
        await client.delete(f"/api/v1/sessions/{session_id}")
        
        # Second attempt to delete should fail
        response = await client.delete(f"/api/v1/sessions/{session_id}")
        
        assert response.status_code == 404  # Not found, not restored


class TestSessionEndpointsOpenAPI:
    """Test Suite: OpenAPI Documentation for Session Endpoints"""
    
    @pytest.mark.asyncio
    async def test_openapi_schema_includes_sessions(self, client):
        """Test that OpenAPI schema includes sessions endpoints."""
        response = await client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        paths = schema.get("paths", {})
        assert "/api/v1/sessions" in paths
    
    @pytest.mark.asyncio
    async def test_post_endpoint_documented(self, client):
        """Test that POST endpoint is documented in OpenAPI."""
        response = await client.get("/openapi.json")
        schema = response.json()
        
        paths = schema.get("paths", {})
        sessions_path = paths.get("/api/v1/sessions", {})
        
        assert "post" in sessions_path
    
    @pytest.mark.asyncio
    async def test_delete_endpoint_documented(self, client):
        """Test that DELETE endpoint is documented in OpenAPI."""
        response = await client.get("/openapi.json")
        schema = response.json()
        
        paths = schema.get("paths", {})
        sessions_path = paths.get("/api/v1/sessions/{session_id}", {})
        
        assert "delete" in sessions_path


class TestSessionEndpointsErrorHandling:
    """Test Suite: Error Handling in Session Endpoints"""
    
    @pytest.mark.asyncio
    async def test_delete_with_uppercase_uuid(self, client):
        """Test that delete accepts uppercase UUID."""
        # Create session
        create_response = await client.post("/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # Delete with uppercase UUID
        uppercase_id = session_id.upper()
        response = await client.delete(f"/api/v1/sessions/{uppercase_id}")
        
        # Should work (UUID is case-insensitive)
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_delete_partial_uuid_returns_422(self, client):
        """Test that partial UUID returns 422."""
        response = await client.delete("/api/v1/sessions/12345")
        
        assert response.status_code == 422
