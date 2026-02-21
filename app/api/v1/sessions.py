"""
FastAPI routes for session management.
Provides endpoints for creating and deleting anonymous sessions.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
    responses={
        503: {"description": "Service unavailable - database connection failed"}
    }
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new anonymous session",
    description="Creates a new anonymous chat session with a unique UUID. Returns session ID and creation timestamp.",
    responses={
        201: {
            "description": "Session created successfully",
            "model": SessionResponse,
        },
        503: {"description": "Database unavailable"},
    }
)
async def create_session(
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """
    Create a new anonymous session.
    
    Creates a new session in the database with a UUID4 identifier.
    No request body is required - client can send empty body or empty JSON object.
    
    Args:
        db: Database session (injected via FastAPI dependency)
        
    Returns:
        SessionResponse with session_id and created_at
        
    Raises:
        HTTPException: 503 if database is unavailable
    """
    try:
        logger.debug("Creating new session...")
        
        # Create new session
        new_session = Session()
        
        # Add to database
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        
        logger.info(f"Session created successfully: {new_session.id}")
        
        return SessionResponse(
            session_id=new_session.id,
            created_at=new_session.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Permanently deletes a session and all associated data. This action cannot be undone.",
    responses={
        204: {"description": "Session deleted successfully"},
        404: {"description": "Session not found"},
        422: {"description": "Invalid session ID format"},
        503: {"description": "Database unavailable"},
    }
)
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a session permanently.
    
    Permanently removes a session from the database. This is a hard delete
    with no recovery possible (user control over data removal).
    
    Args:
        session_id: UUID of the session to delete
        db: Database session (injected via FastAPI dependency)
        
    Raises:
        HTTPException: 404 if session not found
        HTTPException: 422 if session_id format is invalid
        HTTPException: 503 if database is unavailable
    """
    try:
        logger.debug(f"Deleting session: {session_id}")
        
        # Query for the session
        from sqlalchemy import select
        
        result = await db.execute(
            select(Session).where(Session.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if session is None:
            logger.warning(f"Session not found for deletion: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Delete the session
        db.delete(session)
        await db.commit()
        
        logger.info(f"Session deleted successfully: {session_id}")
        
        # Return 204 No Content (implicit)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
