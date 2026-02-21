# BACKEND - HACKTON

## Menjalankan FastAPI (Endpoint Awal)

1. Aktifkan virtual environment:
   - Windows PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
2. Install dependency:
   - `pip install -r requirements.txt`
3. Jalankan server:
   - `python -m uvicorn app.main:app --reload`
4. Uji endpoint awal:
   - Buka `http://127.0.0.1:8000/`
   - Respons yang diharapkan: `{ "message": "hello world" }`
