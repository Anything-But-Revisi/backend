"""
Unit tests for ReportCreate and ReportResponse Pydantic schemas.
Verifies Enum validation, required fields, and serialization.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    LocationEnum,
    PerpBtratorEnum,
    DescriptionEnum,
    EvidenceEnum,
    UserGoalEnum,
)


class TestLocationEnum:
    """Unit tests for LocationEnum validation."""
    
    def test_valid_location_public_space(self):
        """Test valid 'public space' location."""
        report = ReportCreate(
            location="public space",
            perpetrator="stranger",
            description="inappropriate comments",
            evidence="witness",
            user_goal="document safely",
        )
        assert report.location == LocationEnum.PUBLIC_SPACE
    
    def test_valid_location_online(self):
        """Test valid 'online' location."""
        report = ReportCreate(
            location="online",
            perpetrator="colleague",
            description="digital harassment",
            evidence="messages",
            user_goal="understand the risk",
        )
        assert report.location == LocationEnum.ONLINE
    
    def test_valid_location_kampus(self):
        """Test valid 'kampus' location."""
        report = ReportCreate(
            location="kampus",
            perpetrator="lecturer",
            description="unwanted physical touch",
            evidence="none",
            user_goal="explore options",
        )
        assert report.location == LocationEnum.KAMPUS
    
    def test_invalid_location_rejected(self):
        """Test that invalid location values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(
                location="invalid_location",
                perpetrator="colleague",
                description="inappropriate comments",
                evidence="messages",
                user_goal="document safely",
            )
        
        error = exc_info.value.errors()[0]
        assert "location" in error["loc"]
        assert "Input should be 'public space'" in str(error) or "enum" in str(error).lower()


class TestPerpBtratorEnum:
    """Unit tests for PerpBtratorEnum validation."""
    
    def test_valid_perpetrator_supervisor(self):
        """Test valid 'supervisor' perpetrator."""
        report = ReportCreate(
            location="workplace",
            perpetrator="supervisor",
            description="repeated pressure",
            evidence="emails",
            user_goal="document safely",
        )
        assert report.perpetrator == PerpBtratorEnum.SUPERVISOR
    
    def test_invalid_perpetrator_rejected(self):
        """Test that invalid perpetrator values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(
                location="kampus",
                perpetrator="invalid_perpetrator",
                description="inappropriate comments",
                evidence="witness",
                user_goal="document safely",
            )
        
        error = exc_info.value.errors()[0]
        assert "perpetrator" in error["loc"]


class TestDescriptionEnum:
    """Unit tests for DescriptionEnum validation."""
    
    def test_valid_description_inappropriate_comments(self):
        """Test valid 'inappropriate comments' description."""
        report = ReportCreate(
            location="workplace",
            perpetrator="colleague",
            description="inappropriate comments",
            evidence="witness",
            user_goal="document safely",
        )
        assert report.description == DescriptionEnum.INAPPROPRIATE_COMMENTS
    
    def test_valid_description_unwanted_physical_touch(self):
        """Test valid 'unwanted physical touch' description."""
        report = ReportCreate(
            location="kampus",
            perpetrator="lecturer",
            description="unwanted physical touch",
            evidence="witness",
            user_goal="document safely",
        )
        assert report.description == DescriptionEnum.UNWANTED_PHYSICAL_TOUCH
    
    def test_invalid_description_rejected(self):
        """Test that invalid description values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(
                location="online",
                perpetrator="colleague",
                description="invalid_description",
                evidence="messages",
                user_goal="document safely",
            )
        
        error = exc_info.value.errors()[0]
        assert "description" in error["loc"]


class TestEvidenceEnum:
    """Unit tests for EvidenceEnum validation."""
    
    def test_valid_evidence_messages(self):
        """Test valid 'messages' evidence type."""
        report = ReportCreate(
            location="online",
            perpetrator="colleague",
            description="digital harassment",
            evidence="messages",
            user_goal="document safely",
        )
        assert report.evidence == EvidenceEnum.MESSAGES
    
    def test_valid_evidence_none(self):
        """Test valid 'none' evidence type."""
        report = ReportCreate(
            location="workplace",
            perpetrator="supervisor",
            description="threat or coercion",
            evidence="none",
            user_goal="document safely",
        )
        assert report.evidence == EvidenceEnum.NONE
    
    def test_invalid_evidence_rejected(self):
        """Test that invalid evidence values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(
                location="kampus",
                perpetrator="lecturer",
                description="inappropriate comments",
                evidence="invalid_evidence",
                user_goal="document safely",
            )
        
        error = exc_info.value.errors()[0]
        assert "evidence" in error["loc"]


class TestUserGoalEnum:
    """Unit tests for UserGoalEnum validation."""
    
    def test_valid_user_goal_understand_risk(self):
        """Test valid 'understand the risk' user goal."""
        report = ReportCreate(
            location="online",
            perpetrator="stranger",
            description="digital harassment",
            evidence="messages",
            user_goal="understand the risk",
        )
        assert report.user_goal == UserGoalEnum.UNDERSTAND_RISK
    
    def test_valid_user_goal_document_safely(self):
        """Test valid 'document safely' user goal."""
        report = ReportCreate(
            location="workplace",
            perpetrator="colleague",
            description="inappropriate comments",
            evidence="emails",
            user_goal="document safely",
        )
        assert report.user_goal == UserGoalEnum.DOCUMENT_SAFELY
    
    def test_invalid_user_goal_rejected(self):
        """Test that invalid user goal values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(
                location="kampus",
                perpetrator="lecturer",
                description="inappropriate comments",
                evidence="witness",
                user_goal="invalid_goal",
            )
        
        error = exc_info.value.errors()[0]
        assert "user_goal" in error["loc"]


class TestReportCreateSchema:
    """Unit tests for complete ReportCreate schema."""
    
    def test_valid_report_create(self):
        """Test creating a valid ReportCreate instance."""
        report = ReportCreate(
            location="kampus",
            perpetrator="lecturer",
            description="inappropriate comments",
            evidence="witness",
            user_goal="document safely",
        )
        
        assert report.location == LocationEnum.KAMPUS
        assert report.perpetrator == PerpBtratorEnum.LECTURER
        assert report.description == DescriptionEnum.INAPPROPRIATE_COMMENTS
        assert report.evidence == EvidenceEnum.WITNESS
        assert report.user_goal == UserGoalEnum.DOCUMENT_SAFELY
    
    def test_all_enum_combinations_valid(self):
        """Test that all valid Enum combinations can be combined."""
        locations = ["public space", "online", "kampus", "sekolah", "workplace"]
        perpetrators = ["supervisor", "colleague", "lecturer", "client", "stranger"]
        descriptions = [
            "inappropriate comments",
            "unwanted physical touch",
            "repeated pressure",
            "threat or coercion",
            "digital harassment",
        ]
        evidences = ["messages", "emails", "witness", "none"]
        user_goals = ["understand the risk", "document safely", "consider reporting", "explore options"]
        
        # Test each combination doesn't raise ValidationError
        for loc in locations[:2]:  # Test subset for brevity
            for perp in perpetrators[:2]:
                for desc in descriptions[:2]:
                    for evid in evidences[:2]:
                        for goal in user_goals[:2]:
                            report = ReportCreate(
                                location=loc,
                                perpetrator=perp,
                                description=desc,
                                evidence=evid,
                                user_goal=goal,
                            )
                            assert report is not None


class TestReportResponseSchema:
    """Unit tests for ReportResponse schema."""
    
    def test_valid_report_response(self):
        """Test creating a valid ReportResponse instance."""
        session_id = uuid4()
        report_id = uuid4()
        now = datetime.utcnow()
        
        response = ReportResponse(
            id=report_id,
            session_id=session_id,
            location="kampus",
            perpetrator="lecturer",
            description="inappropriate comments",
            evidence="witness",
            user_goal="document safely",
            generated_document="FORMULIR PENGADUAN...",
            created_at=now,
        )
        
        assert response.id == report_id
        assert response.session_id == session_id
        assert response.location == LocationEnum.KAMPUS
        assert response.generated_document == "FORMULIR PENGADUAN..."
    
    def test_report_response_nullable_document(self):
        """Test that generated_document can be null in response."""
        response = ReportResponse(
            id=uuid4(),
            session_id=uuid4(),
            location="online",
            perpetrator="colleague",
            description="digital harassment",
            evidence="messages",
            user_goal="document safely",
            generated_document=None,
            created_at=datetime.utcnow(),
        )
        
        assert response.generated_document is None
    
    def test_missing_required_field_rejected(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ReportResponse(
                id=uuid4(),
                session_id=uuid4(),
                location="kampus",
                # Missing perpetrator field
                description="inappropriate comments",
                evidence="witness",
                user_goal="document safely",
                created_at=datetime.utcnow(),
            )
        
        error = exc_info.value.errors()[0]
        assert "perpetrator" in error["loc"]
