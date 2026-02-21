## ADDED Requirements

### Requirement: Root hello endpoint tersedia

Sistem SHALL menyediakan endpoint HTTP `GET /` pada aplikasi FastAPI untuk memberikan respons awal verifikasi service.

#### Scenario: Request root endpoint berhasil

- **WHEN** client mengirim permintaan `GET /`
- **THEN** sistem merespons status `200`.

### Requirement: Konten respons hello world konsisten

Sistem MUST mengembalikan konten respons yang berisi nilai `hello world` secara konsisten pada setiap permintaan `GET /`.

#### Scenario: Respons memuat hello world

- **WHEN** client menerima respons dari `GET /`
- **THEN** isi respons memuat nilai `hello world` sesuai kontrak API.
