## Why

Backend belum memiliki endpoint awal untuk verifikasi bahwa service berjalan. Menambahkan endpoint sederhana berbasis FastAPI yang mengembalikan `hello world` mempercepat validasi setup, health-check awal, dan onboarding pengembangan.

## What Changes

- Menambahkan aplikasi FastAPI minimal sebagai entrypoint backend.
- Menambahkan endpoint HTTP `GET /` yang mengembalikan respons teks/JSON berisi `hello world`.
- Menyiapkan dependency Python yang dibutuhkan untuk menjalankan FastAPI.
- Tidak ada perubahan breaking pada API yang sudah ada karena ini capability baru.

## Capabilities

### New Capabilities

- `initial-fastapi-hello-endpoint`: Menyediakan endpoint awal FastAPI yang merespons `hello world` untuk verifikasi service.

### Modified Capabilities

- Tidak ada.

## Impact

- Kode terdampak: aplikasi backend Python baru (mis. file entrypoint FastAPI).
- API terdampak: penambahan endpoint `GET /`.
- Dependency: penambahan package FastAPI (dan server ASGI untuk menjalankan aplikasi).
- Sistem terdampak: alur run lokal backend Python.
