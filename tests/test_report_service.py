"""
Unit tests for report generation service.
Tests the generate_report_draft function with mocked Gemini API.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

from app.schemas.report import ReportCreate
from app.services.report import generate_report_draft, retry_report_generation


@pytest.fixture
def sample_report_data():
    """Create sample ReportCreate data for testing."""
    return ReportCreate(
        location="kampus",
        perpetrator="lecturer",
        description="inappropriate comments",
        evidence="witness",
        user_goal="document safely",
    )


@pytest.fixture
def mock_gemini_response():
    """Create a mock Gemini API response."""
    return """## FORMULIR PENGADUAN KEKERASAN SEKSUAL

### I. IDENTIFIKASI KEBUTUHAN
Saya membuat laporan ini untuk mendokumentasikan pengalaman saya dengan aman dan mempertahankan catatan resmi dari insiden yang terjadi.

### II. IDENTIFIKASI PELAKU
Pelaku adalah seorang dosen di institusi pendidikan saya yang memiliki posisi otoritas dalam hubungan akademik kami.

### III. KRONOLOGI KEJADIAN
Saya mengalami komentar-komentar yang tidak pantas dari dosen saya selama beberapa waktu. Perilaku ini telah membuat saya merasa tidak nyaman dan terganggu dalam proses belajar saya.

### IV. BUKTI TERLAMPIR
Saya memiliki saksi yang dapat memberikan keterangan tentang insiden ini."""


@pytest.mark.asyncio
async def test_generate_report_draft_success(sample_report_data, mock_gemini_response):
    """Test successful report generation with mocked Gemini API."""
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        # Setup mock
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = mock_gemini_response
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        result = await generate_report_draft(sample_report_data)
        
        # Assertions
        assert result == mock_gemini_response
        assert "FORMULIR PENGADUAN" in result
        assert "KRONOLOGI KEJADIAN" in result
        mock_model.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_generate_report_draft_uses_correct_system_prompt(sample_report_data, mock_gemini_response):
    """Test that report generation uses the correct system prompt."""
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        # Setup mock
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = mock_gemini_response
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        await generate_report_draft(sample_report_data)
        
        # Verify system_instruction was passed
        call_kwargs = mock_model_class.call_args[1]
        assert "system_instruction" in call_kwargs
        assert "FORMULIR PENGADUAN KEKERASAN SEKSUAL" in call_kwargs["system_instruction"]
        assert "Saya" in call_kwargs["system_instruction"]  # First person perspective


@pytest.mark.asyncio
async def test_generate_report_draft_uses_low_temperature(sample_report_data, mock_gemini_response):
    """Test that report generation uses temperature=0.3 for consistency."""
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        with patch("app.services.report.genai.types.GenerationConfig") as mock_config_class:
            # Setup mock
            mock_model = MagicMock()
            mock_model_class.return_value = mock_model
            mock_response = MagicMock()
            mock_response.text = mock_gemini_response
            mock_model.generate_content.return_value = mock_response
            
            # Call function
            await generate_report_draft(sample_report_data)
            
            # Verify temperature was set to 0.3
            config_call_kwargs = mock_config_class.call_args[1]
            assert config_call_kwargs["temperature"] == 0.3


@pytest.mark.asyncio
async def test_generate_report_draft_no_api_key(sample_report_data):
    """Test that function raises error if API key is not configured."""
    with patch("app.services.report.API_KEY", None):
        with pytest.raises(RuntimeError) as exc_info:
            await generate_report_draft(sample_report_data)
        
        assert "Gemini API key not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_report_draft_api_error(sample_report_data):
    """Test that function raises error if Gemini API call fails."""
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        # Setup mock to raise error
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("API Rate limit exceeded")
        
        with pytest.raises(Exception) as exc_info:
            await generate_report_draft(sample_report_data)
        
        assert "API Rate limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_report_draft_empty_response(sample_report_data):
    """Test that function raises error if Gemini returns empty response."""
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        # Setup mock to return empty response
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError) as exc_info:
            await generate_report_draft(sample_report_data)
        
        assert "empty response" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_report_uses_all_enum_values(mock_gemini_response):
    """Test that all enum values are properly mapped to the prompt."""
    # Create report with all different enum values
    report = ReportCreate(
        location="online",
        perpetrator="colleague",
        description="digital harassment",
        evidence="messages",
        user_goal="understand the risk",
    )
    
    with patch("app.services.report.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = mock_gemini_response
        mock_model.generate_content.return_value = mock_response
        
        await generate_report_draft(report)
        
        # Get the prompt that was sent
        call_args = mock_model.generate_content.call_args[0][0]
        
        # Verify enum values are present in the prompt
        assert "online" in call_args
        assert "colleague" in call_args
        assert "digital harassment" in call_args
        assert "messages" in call_args
        assert "understand the risk" in call_args


@pytest.mark.asyncio
async def test_retry_report_generation_success_on_first_try(sample_report_data, mock_gemini_response):
    """Test retry logic succeeds on first attempt."""
    with patch("app.services.report.generate_report_draft") as mock_generate:
        mock_generate.return_value = mock_gemini_response
        
        result = await retry_report_generation(sample_report_data, max_retries=3)
        
        assert result == mock_gemini_response
        mock_generate.assert_called_once_with(sample_report_data)


@pytest.mark.asyncio
async def test_retry_report_generation_success_after_retry(sample_report_data, mock_gemini_response):
    """Test retry logic succeeds after initial failure."""
    with patch("app.services.report.generate_report_draft") as mock_generate:
        # Fail once, succeed on second attempt
        mock_generate.side_effect = [
            Exception("API Error"),
            mock_gemini_response
        ]
        
        result = await retry_report_generation(sample_report_data, max_retries=3)
        
        assert result == mock_gemini_response
        assert mock_generate.call_count == 2


@pytest.mark.asyncio
async def test_retry_report_generation_fails_after_max_retries(sample_report_data):
    """Test retry logic raises error after max retries exceeded."""
    with patch("app.services.report.generate_report_draft") as mock_generate:
        # Always fail
        mock_generate.side_effect = Exception("Persistent API Error")
        
        with pytest.raises(Exception) as exc_info:
            await retry_report_generation(sample_report_data, max_retries=2)
        
        assert "Persistent API Error" in str(exc_info.value)
        assert mock_generate.call_count == 2
