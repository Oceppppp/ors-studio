# Software Requirements Specification (SRS)
## Operations Research Studio (ORS)

**Dokumen:** ORS-SRS-001  
**Versi:** 0.4.0  
**Tanggal:** 18 November 2026  
**Status:** Dual-distribution public beta foundation  
**Produk:** Public Web (Guest + account) dan Desktop/local

## 1. Tujuan

ORS adalah platform Operations Research, Production and Operations Management, dan Quantitative Methods yang mengintegrasikan katalog baseline 29 modul, input spreadsheet, beberapa analisis dalam satu workspace, visualisasi hasil, serta ekspor laporan. ORS menyediakan dua distribusi: Web yang dapat diakses melalui internet dan Desktop/local yang menyimpan data pada komputer masing-masing.

## 2. Tujuan produk dan prinsip

1. Sediakan satu antarmuka untuk mengakses 29 modul baseline.
2. Izinkan pengguna mengimpor data Excel/CSV; pengguna tidak diwajibkan mengetik ulang seluruh data.
3. Dukung satu analisis maupun batch analisis independen.
4. Pertahankan solver Python yang sama pada Web dan Desktop.
5. Pisahkan data antar pengguna pada Web melalui autentikasi dan otorisasi di backend/database.
6. Pertahankan Desktop yang dapat dijalankan secara lokal tanpa akun Web.
7. Tampilkan asumsi, batas model, dan status solver secara jujur.
8. Gunakan desain Operations Workbench yang berorientasi pada pekerjaan, tabel, dan analisis; hindari pola UI generik yang dekoratif.

## 3. Kategori pengguna

- **Guest Web:** dapat mencoba aplikasi tanpa mendaftarkan email; ruang kerja bersifat sementara dan dihapus setelah masa berlaku.
- **Registered Web User:** membuat akun untuk mempertahankan workspace antarsesi; data tetap privat di bawah principal pemilik.
- **Desktop User:** menggunakan aplikasi lokal pada komputernya tanpa akun Web.
- **Maintainer/Developer:** mengelola source, migrasi, deployment, dan pengembangan solver.

## 4. Scope modul

ORS mempertahankan 29 module keys pada `MODULE_CATALOG.md`. Cakupan algoritma yang benar-benar disediakan setiap key dijelaskan pada `MODULE_IMPLEMENTATION_SCOPE.md`. Ketersediaan 29 key tidak berarti kesetaraan penuh seluruh submodel atau laporan setiap versi POM-QM. Tidak boleh mengklaim paritas penuh tanpa pembandingan dengan versi target dan test vectors independen.

## 5. Distribusi dan runtime

### 5.1 Public Web

- Frontend dan API tersedia dari satu origin HTTPS.
- Pengunjung dapat memilih Guest, membuat akun, atau login.
- Setelah autentikasi, pengguna mendapat workspace pribadi.
- Web memakai FastAPI `orstudio.web_api:app`, PostgreSQL, Redis/RQ, dan private worker.
- Analisis batch dijalankan pada worker, bukan pada proses request web.
- Web service tidak memakai SQLite atau filesystem ephemeral sebagai penyimpanan data produksi.

### 5.2 Desktop/local

- Aplikasi berjalan di komputer pengguna dan membuka UI melalui browser lokal.
- API lokal memakai `orstudio.api:app` dan SQLite.
- API hanya boleh bind ke `127.0.0.1`.
- Akun Web tidak diwajibkan.
- Installer mandiri Windows ditargetkan agar pengguna akhir tidak perlu memasang Python atau dependensi secara manual. Installer belum dianggap tersedia sebelum workflow Windows sukses dan clean-machine test lulus.

## 6. Fitur fungsional — status v0.4.0

| ID | Requirement | Web | Desktop |
|---|---|---|---|
| FR-001 | Menampilkan katalog 29 modul baseline | Implemented | Implemented |
| FR-002 | Memilih parameter dan menjalankan satu analisis | Implemented | Implemented |
| FR-003 | Upload CSV/XLSX, preview, dan memilih worksheet | Implemented | Implemented |
| FR-004 | Memetakan kolom numerik ke parameter model | Implemented | Implemented |
| FR-005 | Menjalankan beberapa job independen dalam batch | Implemented (RQ) | Implemented (bounded local pool) |
| FR-006 | Memantau status, membuka hasil, dan mengekspor | Implemented | Implemented |
| FR-007 | Membandingkan forecasting dengan holdout | Implemented | Implemented |
| FR-008 | Menjalankan tanpa akun melalui Guest Mode | Implemented | Not applicable |
| FR-009 | Membuat akun/login dengan password hash | Implemented (beta; no email verification) | Not applicable |
| FR-010 | Mengupgrade guest ke akun tanpa kehilangan workspace | Implemented | Not applicable |
| FR-011 | Memisahkan proyek/dataset/analisis/job tiap principal | Implemented; regression test | Local OS profile isolation |
| FR-012 | Menyimpan proyek lintas kunjungan di PostgreSQL | Implemented | Local SQLite persistence |
| FR-013 | Men-deploy Web melalui blueprint hosting | Prepared; not deployed | Not applicable |
| FR-014 | Membangun installer Windows mandiri | Workflow prepared; not yet verified | Workflow prepared; not yet verified |

## 7. Guest and account limits

### Guest
- Masa sesi: 24 jam.
- Maksimum dua project/workspace termasuk default.
- Maksimum tiga dataset, 5 MiB per upload, dan 15 MiB total penyimpanan dataset yang telah dinormalisasi.
- Maksimum 10.000 baris per dataset.
- Maksimum lima job per batch dan sepuluh analisis/job tersimpan.
- Guest dapat mengupgrade ke akun; project dan dataset yang sudah ada tetap dimiliki principal yang sama.

### Registered account
- Masa sesi: 14 hari.
- Default beta: 50 project, 100 dataset, upload maksimum 20 MiB, total penyimpanan dataset 250 MiB, batch maksimum 40 task, 1.000 queued jobs dan 5.000 saved analyses.
- Quota perlu dievaluasi melalui uji beban dan konfigurasi sebelum jumlah pengguna besar.

## 8. Data import dan persistence

- Format sumber: CSV dan XLSX.
- File dibaca dan divalidasi; worksheet dapat dipilih.
- Data yang dinormalisasi disimpan bersama project pemilik.
- Pada Web v0.4.0, original workbook binary tidak dipertahankan setelah parsing; kolom/baris hasil parsing disimpan di PostgreSQL.
- Data Desktop disimpan pada SQLite lokal user.
- Workbook formulas/macros/scripts tidak dieksekusi.
- File upload harus memenuhi batas byte, jumlah sheet/member ZIP, expanded size, baris, kolom, dan cell count pada import service.

## 9. Batch dan solver execution

- Pengguna dapat menambahkan beberapa model independen ke satu batch.
- Semua task divalidasi sebelum records disimpan.
- Web mengirim job ke Redis/RQ; private worker menjalankan solver yang sama dengan Desktop.
- Desktop menggunakan bounded worker pool lokal.
- Job yang masih queued dapat dibatalkan; running solver cancellation belum dijamin aman.
- Workflow DAG, dependensi antar-analisis, dan output-to-input chaining belum tersedia.

## 10. Results and export

Output dapat meliputi ringkasan solusi, tabel, grafik, input snapshot, dataset provenance, asumsi/model limits, status, dan error. Ekspor Excel, CSV, serta PDF dihasilkan untuk hasil yang sudah tersimpan dan dapat diakses oleh pemiliknya.

Forecast comparison menggunakan holdout yang sebanding. Default selection memilih MAD terkecil, lalu MSE sebagai tie-break. Jangan menyebut metode terbaik untuk sampel atau objective yang tidak sebanding.

## 11. Security and privacy requirements

- Password akun disimpan sebagai Argon2 hash; tidak pernah sebagai plaintext.
- Browser session token bersifat random opaque; database hanya menyimpan HMAC-SHA256 digest.
- Cookie: HttpOnly, SameSite=Lax, Secure pada production.
- Setiap query data Web wajib memeriksa kepemilikan principal melalui project owner.
- Mutating browser request lintas origin ditolak; CORS tidak dibuka ke sembarang origin.
- Login, register, dan guest creation dibatasi rate limit melalui Redis di production.
- Guest data dibersihkan setelah 24 jam.
- Jangan simpan secret, dump DB, workbook pengguna, atau session token di repository.
- Email verification, password reset, formal self-service deletion/export, dan independent security audit belum tersedia; lihat `SECURITY_MODEL.md`.

## 12. Deployment and operations

- `render.yaml` mendefinisikan Web service, worker, PostgreSQL, private Key Value/Redis, dan guest cleanup cron.
- Web dan worker memakai versi kode dan database yang sama.
- PostgreSQL schema dikelola oleh Alembic.
- HTTPS, backup, observability, restore testing, rate-limit monitoring, and capacity testing diperlukan sebelum production promotion.
- Blueprint belum berarti deployment sudah live; domain, account, biaya, dan provisioning harus dikonfirmasi pada akun hosting.

## 13. Non-functional requirements

- **Correctness:** solver outputs must match documented model assumptions and independently verified reference cases.
- **Isolation:** one principal cannot read or mutate another principal's cloud objects.
- **Availability:** worker and database health should be monitored; no SLA is claimed for beta.
- **Performance:** imports and solvers must have bounded upload, input, and worker limits.
- **Maintainability:** frontend, APIs, stores, import/export, orchestrator, queue, and solver modules remain separated.
- **Portability:** Desktop source targets Python 3.15.x; packaged Windows build must be verified on a clean machine.
- **Accessibility:** keyboard focus, semantic controls, validation messages, and responsive layout are required.

## 14. Acceptance and verification

Current source tests are recorded in `docs/IMPLEMENTATION_STATUS.md`. Web acceptance tests must cover Guest, register/login, guest upgrade, cross-tenant object isolation, imports, single analysis, batch worker completion, exports, and cross-origin rejection. Desktop must be tested separately on clean Windows. Public deployment must verify Render health, real PostgreSQL and Redis connectivity, HTTPS cookies, guest cleanup, backup/restore, and two-user isolation using distinct browser profiles.

## 15. Release limitations

v0.4.0 is a **public beta foundation / deployment candidate**. It is not yet a fully production-audited service. Do not advertise verified email, password recovery, user-managed deletion/export, original file archival, multi-analysis DAG, full POM-QM parity, or a published installer until each is implemented and verified.
