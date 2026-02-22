import os
import logging
import google.generativeai as genai
from typing import List, Dict

logger = logging.getLogger(__name__)

# Task 3.2 - 3.4: Inisialisasi dan System Prompt
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GOOGLE_API_KEY tidak ditemukan di environment variables.")

SYSTEM_INSTRUCTION = """
Kamu adalah pendamping empatik di platform SafeSpace, sebuah ruang aman bagi penyintas kekerasan seksual.
Tugas utamamu adalah mendengarkan, memvalidasi perasaan pengguna, dan memberikan dukungan emosional awal.
Gunakan bahasa Indonesia yang sopan, lembut, dan menenangkan. 
Jangan pernah menghakimi, menyalahkan, atau memaksa pengguna bercerita jika mereka belum siap.
Fokus pada perasaan mereka saat ini. Jika ada indikasi bahaya darurat, sarankan mereka menghubungi profesional dengan lembut.
"""

def get_gemini_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

def format_history(db_messages) -> List[Dict]:
    """Mengonversi format riwayat DB menjadi format yang dipahami API Gemini."""
    return [
        {"role": msg.role, "parts": [msg.content]} 
        for msg in db_messages if msg.role in ["user", "model"]
    ]

# Task 3.5 & 3.6: Panggil API dengan konteks history dan error handling
async def generate_chat_response(message: str, history=None) -> str:
    if not API_KEY:
        return "Maaf, sistem AI sedang tidak terhubung (API Key hilang). Silakan hubungi admin."
    
    try:
        model = get_gemini_model()
        formatted_history = format_history(history) if history else []
        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return "Maaf, saya sedang kesulitan memproses pesanmu. Bisakah kamu mengulanginya perlahan?"