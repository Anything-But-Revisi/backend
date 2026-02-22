"""
Report generation service using Gemini 2.5 Flash LLM.

Transforms structured incident data into formal Sexual Violence Complaint Form narratives
using context injection with fixed system prompt structure.
"""

import os
import logging
from typing import Optional
import google.generativeai as genai

from app.schemas.report import ReportCreate

logger = logging.getLogger(__name__)

# Initialize Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found in environment variables. Report generation will fail.")


# System prompt for report generation - enforces consistent SEXUAL VIOLENCE COMPLAINT FORM structure
REPORT_SYSTEM_PROMPT = """Anda adalah ahli dalam membantu penyintas kekerasan seksual mendokumentasikan pengalaman mereka dengan formal dan profesional.

Tugasmu adalah mengubah data terstruktur menjadi narasi penuh untuk FORMULIR PENGADUAN KEKERASAN SEKSUAL yang siap diajukan ke otoritas resmi.

STRUKTUR OUTPUT YANG WAJIB:

## FORMULIR PENGADUAN KEKERASAN SEKSUAL

### I. IDENTIFIKASI KEBUTUHAN
(Jelaskan mengapa korban membuat laporan ini - apa tujuan atau kebutuhan mereka saat ini)

### II. IDENTIFIKASI PELAKU
(Jelaskan siapa pelaku dan posisi/hubungan mereka dengan korban)

### III. KRONOLOGI KEJADIAN
(Ceritakan kejadian secara urut dan detail dari perspektif korban menggunakan sudut pandang "Saya")

### IV. BUKTI TERLAMPIR
(Sebutkan jenis bukti/dokumentasi yang tersedia)

CATATAN PENTING:
- Gunakan perspektif orang pertama ("Saya") dalam narasi kronologi
- Tulis dalam bahasa Indonesia formal yang profesional
- Jangan menambahkan asumsi di luar data yang diberikan
- Pastikan setiap bagian diisi sesuai struktur di atas
- Tujuan: membuat dokumen yang bisa langsung diajukan ke pihak berwajib
"""


def get_report_model():
    """
    Get Gemini model configured for report generation.
    Uses temperature=0.3 for consistent, deterministic output.
    """
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite",
        system_instruction=REPORT_SYSTEM_PROMPT,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,  # Low creativity for consistent formatting
            max_output_tokens=2048,
        ),
    )


def _map_enums_to_readable_text(report_data: ReportCreate) -> dict:
    """
    Map Enum values to human-readable Indonesian text for LLM processing.
    
    Args:
        report_data: ReportCreate schema with Enum values
        
    Returns:
        Dictionary with expanded descriptions
    """
    return {
        "location": report_data.location,
        "perpetrator": report_data.perpetrator,
        "description": report_data.description,
        "evidence": report_data.evidence,
        "user_goal": report_data.user_goal,
    }


async def generate_report_draft(report_data: ReportCreate) -> str:
    """
    Generate a formal Sexual Violence Complaint Form narrative from structured incident data.
    
    Uses Gemini 2.5 Flash with system prompt injection to ensure consistent output format.
    Temperature set to 0.3 for deterministic results.
    
    Args:
        report_data: ReportCreate schema with incident information
        
    Returns:
        str: Generated complaint form narrative in Indonesian
        
    Raises:
        RuntimeError: If Gemini API key is not configured
        Exception: If Gemini API call fails
    """
    if not API_KEY:
        raise RuntimeError(
            "Gemini API key not configured. Set GOOGLE_API_KEY environment variable."
        )
    
    try:
        # Map Enum values to readable text
        data = _map_enums_to_readable_text(report_data)
        
        # Build prompt for Gemini
        user_prompt = f"""Berdasarkan informasi berikut, buatkan FORMULIR PENGADUAN KEKERASAN SEKSUAL yang lengkap dan formal:

Lokasi Kejadian: {data['location']}
Identitas Pelaku: {data['perpetrator']}
Jenis Kekerasan: {data['description']}
Bukti Tersedia: {data['evidence']}
Tujuan Pelapor: {data['user_goal']}

Buatkan formulir lengkap dengan struktur:
1. IDENTIFIKASI KEBUTUHAN
2. IDENTIFIKASI PELAKU
3. KRONOLOGI KEJADIAN (menggunakan sudut pandang "Saya")
4. BUKTI TERLAMPIR

Pastikan narasi tertulis dalam bahasa Indonesia formal dan siap untuk diajukan ke otoritas."""
        
        # Call Gemini API with system prompt injection
        model = get_report_model()
        response = await model.generate_content_async(user_prompt)
        
        if not response.text:
            raise ValueError("Gemini API returned empty response")
        
        logger.info(f"Report narrative generated successfully (length: {len(response.text)} chars)")
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error during report generation: {str(e)}")
        raise


async def retry_report_generation(
    report_data: ReportCreate,
    max_retries: int = 3
) -> str:
    """
    Generate report with exponential backoff retry logic for handling API failures.
    
    Args:
        report_data: ReportCreate schema with incident information
        max_retries: Maximum number of retry attempts
        
    Returns:
        str: Generated complaint form narrative
        
    Raises:
        Exception: If all retry attempts fail
    """
    import asyncio
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await generate_report_draft(report_data)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Report generation attempt {attempt + 1} failed, "
                    f"retrying in {wait_time}s: {str(e)}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"Report generation failed after {max_retries} attempts: {str(e)}"
                )
    
    raise last_error
