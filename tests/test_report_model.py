"""
Unit tests for Report model and relationships.
Verifies ORM model structure, foreign key constraints, and session relationship.
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models.session import Base, Session
from app.models.report import Report


@pytest.fixture
async def test_db():
    """Create an in-memory SQLite test database with async support."""
    # Use SQLite with async support for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield async_session_factory
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_report_model_creation(test_db):
    """Test that Report model can be instantiated with valid data."""
    session_factory = test_db
    
    async with session_factory() as session:
        # Create a session first
        test_session = Session()
        session.add(test_session)
        await session.commit()
        await session.refresh(test_session)
        
        # Create a report
        report = Report(
            session_id=test_session.id,
            location="kampus",
            perpetrator="lecturer",
            description="inappropriate comments",
            evidence="witness",
            user_goal="document safely",
            generated_document=None,
        )
        
        session.add(report)
        await session.commit()
        await session.refresh(report)
        
        # Verify report was created
        assert report.id is not None
        assert report.session_id == test_session.id
        assert report.location == "kampus"
        assert report.perpetrator == "lecturer"
        assert report.created_at is not None


@pytest.mark.asyncio
async def test_report_relationship_to_session(test_db):
    """Test that Report model has correct relationship to Session."""
    session_factory = test_db
    
    async with session_factory() as session:
        # Create a session
        test_session = Session()
        session.add(test_session)
        await session.commit()
        await session.refresh(test_session)
        
        # Create reports
        report1 = Report(
            session_id=test_session.id,
            location="online",
            perpetrator="colleague",
            description="digital harassment",
            evidence="messages",
            user_goal="understand the risk",
        )
        report2 = Report(
            session_id=test_session.id,
            location="workplace",
            perpetrator="supervisor",
            description="unwanted physical touch",
            evidence="none",
            user_goal="consider reporting",
        )
        
        session.add(report1)
        session.add(report2)
        await session.commit()
        
        # Query session and check relationship
        from sqlalchemy import select
        result = await session.execute(
            select(Session).where(Session.id == test_session.id)
        )
        fetched_session = result.scalar_one()
        
        # Verify back-relationship works
        assert len(fetched_session.reports) == 2
        assert report1 in fetched_session.reports
        assert report2 in fetched_session.reports


@pytest.mark.asyncio
async def test_report_cascade_delete(test_db):
    """Test that cascade delete removes reports when session is deleted."""
    session_factory = test_db
    
    async with session_factory() as session:
        # Create a session
        test_session = Session()
        session.add(test_session)
        await session.commit()
        session_id = test_session.id
        
        # Create reports
        report1 = Report(
            session_id=session_id,
            location="public space",
            perpetrator="stranger",
            description="threat or coercion",
            evidence="emails",
            user_goal="explore options",
        )
        session.add(report1)
        await session.commit()
        
        # Query to get counts
        from sqlalchemy import select, func
        
        # Verify report exists
        result = await session.execute(
            select(func.count(Report.id)).where(Report.session_id == session_id)
        )
        report_count = result.scalar()
        assert report_count == 1
        
        # Delete the session
        result = await session.execute(
            select(Session).where(Session.id == session_id)
        )
        session_to_delete = result.scalar_one()
        await session.delete(session_to_delete)
        await session.commit()
        
        # Verify reports are deleted (cascade)
        result = await session.execute(
            select(func.count(Report.id)).where(Report.session_id == session_id)
        )
        report_count_after = result.scalar()
        assert report_count_after == 0


@pytest.mark.asyncio
async def test_report_nullable_generated_document(test_db):
    """Test that generated_document field can be null."""
    session_factory = test_db
    
    async with session_factory() as session:
        # Create a session
        test_session = Session()
        session.add(test_session)
        await session.commit()
        
        # Create report without generated_document
        report = Report(
            session_id=test_session.id,
            location="sekolah",
            perpetrator="colleague",
            description="repeated pressure",
            evidence="witness",
            user_goal="document safely",
            # generated_document is None by default
        )
        
        session.add(report)
        await session.commit()
        await session.refresh(report)
        
        # Verify generated_document is null
        assert report.generated_document is None
        
        # Update with generated document
        generated_text = "FORMULIR PENGADUAN KEKERASAN SEKSUAL..."
        report.generated_document = generated_text
        await session.commit()
        await session.refresh(report)
        
        # Verify generated_document is now populated
        assert report.generated_document == generated_text
