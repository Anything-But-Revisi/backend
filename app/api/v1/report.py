"""
FastAPI routes for report (incident form) management.
Provides endpoints for creating and retrieving Sexual Violence Complaint Form reports.
Reports are scoped to sessions with automatic Gemini-powered narrative generation.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.session import Session
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse
from app.services.report import generate_report_draft

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sessions",
    tags=["Reports"],
    responses={
        404: {"description": "Session or report not found"},
        422: {"description": "Invalid request data"},
        503: {"description": "Database or service unavailable"},
    }
)


async def _verify_session_exists(session_id: UUID, db: AsyncSession) -> Session:
    """
    Verify that a session exists in the database.
    
    Args:
        session_id: UUID of the session to verify
        db: Database session
        
    Returns:
        Session object
        
    Raises:
        HTTPException: 404 if session not found
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return session


@router.post(
    "/{session_id}/report",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create and generate a Sexual Violence Complaint Form",
    description="Accepts structured incident data, generates a formal complaint form narrative using Gemini LLM, and stores the report.",
    responses={
        201: {
            "description": "Report created and narrative generated successfully",
            "model": ReportResponse,
        },
        404: {"description": "Session not found"},
        422: {"description": "Invalid Enum values in request"},
        500: {"description": "Report generation failed but data was saved"},
        503: {"description": "Database unavailable"},
    }
)
async def create_report(
    session_id: UUID,
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """
    Create a new incident report and generate complaint form narrative.
    
    Accepts structured incident data with Enum validation, saves to database,
    calls Gemini to generate formal complaint form narrative, and returns complete report.
    
    Args:
        session_id: UUID of the parent session
        report_data: ReportCreate schema with incident information
        db: Database session (injected via FastAPI dependency)
        
    Returns:
        ReportResponse with all report fields including generated_document
        
    Raises:
        HTTPException: 404 if session not found
        HTTPException: 422 if Enum validation fails
        HTTPException: 500 if Gemini generation fails
        HTTPException: 503 if database is unavailable
    """
    try:
        logger.debug(f"Creating report for session: {session_id}")
        
        # Verify session exists
        await _verify_session_exists(session_id, db)
        
        # Create report record with input data
        new_report = Report(
            session_id=session_id,
            location=report_data.location,
            perpetrator=report_data.perpetrator,
            description=report_data.description,
            evidence=report_data.evidence,
            user_goal=report_data.user_goal,
            generated_document=None,  # Will be populated after Gemini generation
        )
        
        # Save report to database (with null generated_document)
        db.add(new_report)
        await db.commit()
        await db.refresh(new_report)
        
        logger.info(f"Report record created: {new_report.id}")
        
        # Generate complaint form narrative using Gemini
        try:
            generated_narrative = await generate_report_draft(report_data)
            
            # Update report with generated document
            new_report.generated_document = generated_narrative
            db.add(new_report)
            await db.commit()
            await db.refresh(new_report)
            
            logger.info(f"Report narrative generated and saved: {new_report.id}")
            
        except Exception as e:
            logger.error(f"Gemini generation failed for report {new_report.id}: {str(e)}")
            # Report data is saved; generated_document remains null
            # Return 500 to indicate generation failed but data was preserved
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Report created but narrative generation failed: {str(e)}"
            )
        
        return ReportResponse.model_validate(new_report)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to create report for session {session_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ERROR ASLI: {str(e)}"  # <--- UBAH BARIS INI
        )


@router.get(
    "/{session_id}/report",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve an existing report",
    description="Retrieves the Sexual Violence Complaint Form report for a given session.",
    responses={
        200: {
            "description": "Report retrieved successfully",
            "model": ReportResponse,
        },
        404: {"description": "Session or report not found"},
        422: {"description": "Invalid session ID format"},
        503: {"description": "Database unavailable"},
    }
)
async def get_report(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    """
    Retrieve the report for a given session.
    
    Args:
        session_id: UUID of the session
        db: Database session (injected via FastAPI dependency)
        
    Returns:
        ReportResponse with complete report data
        
    Raises:
        HTTPException: 404 if session not found or no report exists for session
        HTTPException: 422 if session_id format is invalid
        HTTPException: 503 if database is unavailable
    """
    try:
        logger.debug(f"Retrieving report for session: {session_id}")
        
        # Verify session exists
        await _verify_session_exists(session_id, db)
        
        # Query for report
        result = await db.execute(
            select(Report).where(Report.session_id == session_id)
        )
        report = result.scalar_one_or_none()
        
        if report is None:
            logger.warning(f"No report found for session: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No report found for session {session_id}"
            )
        
        logger.info(f"Report retrieved: {report.id}")
        
        return ReportResponse.model_validate(report)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve report for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
