# ORS Studio 0.4.0

**Operations Research Studio** adalah platform analisis Operations Research dan Quantitative Methods dengan dua jalur penggunaan: Web publik (Guest Mode atau akun) dan Desktop lokal/offline. Katalog baseline berisi 29 modul analisis; setiap modul menampilkan cakupan model dan batasan implementasinya.

## Pilih cara menggunakan

### Public Web (multi-user)

Web edition menggunakan FastAPI, PostgreSQL, Redis/RQ worker, dan sesi berbasis cookie HttpOnly. Setiap proyek dimiliki satu principal (akun atau guest) dan semua query data proyek dibatasi dengan `owner_id`. Guest dapat langsung mencoba tanpa login; guest memiliki batas penyimpanan dan sesi 24 jam. Akun dapat mendaftar dan login.

Untuk menjalankan lokal dengan Docker: salin `.env.example` ke `.env`, ganti secret development, lalu jalankan:

```bash
docker compose -f compose.web.yaml up --build
```

Buka `http://localhost:8000`. Migrasi database: `alembic upgrade head`. Worker menjalankan job queue terpisah.

Untuk deployment publik, gunakan `render.yaml` sebagai Render Blueprint. Baca [Panduan Deployment Web](docs/WEB_DEPLOYMENT.md) dan [Model Keamanan](docs/SECURITY_MODEL.md). Konfigurasi ini membuat FastAPI web service, PostgreSQL, Redis-compatible Key Value, background worker, dan jadwal pembersihan guest.

### Desktop (lokal/offline)

Pengguna dapat menggunakan aplikasi lokal tanpa akun. Data tersimpan di profil komputer masing-masing menggunakan SQLite. Setup Windows mendukung Python 3.15.2 untuk source mode; installer release membundel runtime dan dependensi.

- Windows source setup: `setup_windows.bat` lalu `START_ORS.bat`.
- Linux/macOS source development: gunakan `run_local.sh` dan dokumentasi developer.

## Modul dan fitur

- 29 modul pada katalog baseline Operations Research / Production & Operations Management / Quantitative Methods.
- Upload `.xlsx` dan `.csv`, preview, validasi, worksheet selection, serta column mapping.
- Single analysis dan batch job processing.
- Forecast method comparison: MAD, MSE, RMSE, MAPE dan pemilihan metode berdasarkan holdout MAD.
- Hasil analisis dan ekspor Excel, CSV, PDF.
- Web mode: guest dan akun, personal workspace, PostgreSQL tenancy separation.

## Development & testing

```bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=backend python -m pytest -q
```

Cloud/web test dependencies: `requirements-web.txt`. Python cloud runtime ditetapkan ke 3.13.5 pada Render; Windows desktop source mendukung Python 3.15.2.

## Dokumentasi

- [Panduan Pengguna](docs/PANDUAN_PENGGUNA.md)
- [Web Deployment](docs/WEB_DEPLOYMENT.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Cloud Architecture](docs/CLOUD_ARCHITECTURE.md)
- [Technical Architecture](docs/TAD.md)
- [Module Implementation Scope](docs/MODULE_IMPLEMENTATION_SCOPE.md)
- [UI Design Review](docs/UI_DESIGN_REVIEW.md)
- [Release & GitHub](docs/RELEASE_AND_GITHUB.md)

## Status rilis

ORS Studio 0.4.0 menambahkan fondasi Public Web multi-user. Kode dan automated tests dapat diuji secara lokal. Deployment live, email verification/password recovery, security review independen, load testing, dan installer Windows yang dibangun oleh GitHub Actions harus diverifikasi sebelum disebut production-ready.
