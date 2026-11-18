# ORS Studio 0.4.0

**Operations Research Studio** adalah platform Operations Research dan Quantitative Methods dengan dua jalur penggunaan: Web publik (Guest Mode atau akun) dan Desktop lokal/offline. Katalog baseline berisi 29 modul analisis; setiap modul menampilkan cakupan model dan batasan implementasinya.

## Pilih cara menggunakan ORS

### Public Web (multi-user)

Web edition menggunakan FastAPI, PostgreSQL, Redis/RQ worker, dan sesi berbasis cookie HttpOnly. Setiap proyek dimiliki satu principal (akun atau guest) dan semua query data proyek dibatasi dengan owner_id. Guest dapat langsung mencoba tanpa login; guest memiliki batas penyimpanan dan sesi 24 jam. Akun dapat mendaftar dan login.

### Deployment publik: Netlify + Railway

- **Netlify** menjadi hosting frontend statis dari folder frontend.
- **Railway** menjalankan backend Python FastAPI, PostgreSQL, Redis, private RQ worker, dan guest cleanup terjadwal.
- Netlify melakukan rewrite request browser dari /api/* ke Railway API supaya cookie sesi tetap same-origin dari sudut pandang browser.
- API dan worker menggunakan PostgreSQL, Redis, serta solver registry yang sama.

Ikuti [Panduan Deployment Netlify + Railway](docs/RAILWAY_NETLIFY_DEPLOYMENT.md). Repository sudah menyertakan netlify.toml, script proxy saat build, Dockerfile Railway, dan railway.toml.

### Web development lokal

Salin .env.example menjadi .env, ganti development session secret, lalu jalankan:

~~~bash
docker compose -f compose.web.yaml up --build
~~~

Buka http://localhost:8000. Jalankan migrasi dengan alembic upgrade head. Worker berjalan terpisah dari HTTP process.

### Desktop (lokal/offline)

Pengguna dapat menggunakan aplikasi lokal tanpa akun. Data tersimpan di profil komputer masing-masing menggunakan SQLite. Setup Windows mendukung Python 3.15.2 untuk source mode; installer release membundel runtime dan dependensi.

- Windows source setup: setup_windows.bat lalu START_ORS.bat.
- Linux/macOS source development: gunakan run_local.sh dan dokumentasi developer.

## Modul dan fitur

- 29 modul katalog baseline Operations Research, POM, dan Quantitative Methods.
- Import XLSX dan CSV, preview, validasi, pemilihan worksheet, dan column mapping.
- Single analysis dan batch processing.
- Forecast comparison dengan MAD, MSE, RMSE, MAPE, dan pemilihan metode berdasarkan holdout MAD.
- Hasil analisis serta export Excel, CSV, dan PDF.
- Web multi-user dengan Guest/Account Mode, personal workspace, dan isolasi tenant PostgreSQL.

## Development dan testing

~~~bash
python -m pip install -r requirements-dev.txt
PYTHONPATH=backend python -m pytest -q
~~~

Dependensi Web ada di requirements-web.txt. Runtime cloud Railway menggunakan Python 3.13.5; source Desktop Windows menggunakan Python 3.15.2.

## Dokumentasi

- [Panduan Pengguna](docs/PANDUAN_PENGGUNA.md)
- [Panduan Deployment Netlify + Railway](docs/RAILWAY_NETLIFY_DEPLOYMENT.md)
- [Arsitektur Cloud](docs/CLOUD_ARCHITECTURE.md)
- [Model Keamanan](docs/SECURITY_MODEL.md)
- [Technical Architecture](docs/TAD.md)
- [Cakupan Implementasi Modul](docs/MODULE_IMPLEMENTATION_SCOPE.md)
- [UI Design Review](docs/UI_DESIGN_REVIEW.md)
- [Release & GitHub](docs/RELEASE_AND_GITHUB.md)

## Status rilis

ORS Studio 0.4.0 menyediakan fondasi Web multi-user. Source dan automated tests dapat dijalankan secara lokal. Deployment publik, email verification/password recovery, independent security review, load testing, dan installer Windows hasil GitHub Actions masih harus diverifikasi sebelum layanan dinyatakan production-ready.
