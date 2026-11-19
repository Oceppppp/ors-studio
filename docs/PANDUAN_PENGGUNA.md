# Panduan Pengguna — ORS Studio v0.4.0

ORS dapat digunakan dalam dua jalur yang terpisah:

1. **Desktop/local mode (cara utama untuk mulai mencoba):** aplikasi dijalankan dari terminal di komputer sendiri, menggunakan SQLite lokal, tanpa akun cloud.
2. **Public Web mode (opsional):** Guest atau Account menggunakan backend cloud yang dideploy terpisah. URL publik hanya tersedia setelah deployment berhasil.

## A. Mulai menggunakan Desktop/local mode

### Windows 10/11

1. Unduh source melalui GitHub: https://github.com/Oceppppp/ors-studio → Code → Download ZIP.
2. Ekstrak ZIP ke folder pada komputer.
3. Pasang Python 3.15.x 64-bit dari https://www.python.org/downloads/windows/ dan pastikan Python Launcher terpasang.
4. Periksa melalui Command Prompt:

~~~cmd
py -3.15 --version
~~~

5. Jalankan setup_windows.bat melalui File Explorer atau Command Prompt.
6. Setelah muncul pesan Setup complete, jalankan START_ORS.bat.
7. Browser akan membuka alamat lokal. Biarkan terminal tetap terbuka selama aplikasi dipakai.

Panduan rinci: [QUICK_START_TERMINAL_ID.md](QUICK_START_TERMINAL_ID.md).

Jangan memasukkan perintah .bat ke Python Shell yang menampilkan >>>.

### macOS / Linux

Dari folder repository, jalankan:

~~~bash
chmod +x run_local.sh
./run_local.sh
~~~

Script menyiapkan virtual environment dan dependensi lokal jika belum ada. Lihat Developer Guide untuk detail lingkungan Python pada sistem operasi Anda.

## B. Memahami penyimpanan lokal

- Windows: %LOCALAPPDATA%/ORS-Studio.
- macOS/Linux: ~/.ors-studio secara default.
- Setiap komputer menyimpan data sendiri.
- Data tidak otomatis disinkronkan ke komputer teman.
- Backend lokal hanya bind ke 127.0.0.1 dan bukan server publik.

Untuk menggunakan ORS, setiap teman mengunduh repository dan menjalankan instalasi pada komputernya sendiri. Link GitHub untuk dibagikan: https://github.com/Oceppppp/ors-studio.

## C. Menggunakan aplikasi

1. Buka Analysis Modules dan pilih modul yang sesuai dengan permasalahan.
2. Masukkan parameter secara manual atau siapkan dataset CSV/XLSX.
3. Buka Data Center untuk memeriksa dan mengimpor dataset.
4. Periksa column mapping dan asumsi model.
5. Jalankan satu analisis atau tambahkan beberapa pekerjaan ke batch lokal.
6. Periksa hasil, grafik, dan riwayat.
7. Ekspor hasil ke Excel, CSV, atau PDF.

## D. Cakupan modul dan batasan

Katalog baseline memiliki 29 module keys. Ketersediaan suatu module key tidak berarti seluruh submodel lanjutan pada semua versi POM-QM sudah direplikasi. Periksa docs/MODULE_IMPLEMENTATION_SCOPE.md untuk metode, asumsi, dan batasan solver sebelum memakai hasil.

## E. Public Web mode (opsional)

Web mode menyediakan Guest/Account, workspace berbasis pemilik, PostgreSQL, Redis/RQ queue, dan worker. Web mode memerlukan deployment cloud tersendiri. Kode konfigurasi Netlify + Railway tersedia di docs/RAILWAY_NETLIFY_DEPLOYMENT.md, tetapi tidak diperlukan untuk menjalankan Desktop/local mode.

Akun Web beta belum memiliki verifikasi email dan pemulihan password. Jangan menyimpan data sensitif perusahaan atau pribadi sebelum kebijakan privasi, proses penghapusan data, dan audit keamanan publik selesai.

## F. Menghentikan aplikasi

Pada terminal yang menjalankan ORS, tekan Ctrl+C. Jangan menutup terminal jika masih ingin memakai aplikasi.
