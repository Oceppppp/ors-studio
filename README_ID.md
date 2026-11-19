# ORS Studio 0.4.0

**Operations Research Studio** adalah aplikasi modular untuk Operations Research dan Quantitative Methods dengan 29 modul analisis terdaftar. Cara paling mudah untuk mencoba ORS adalah menjalankannya secara lokal melalui terminal. Setiap orang menjalankan salinan aplikasinya sendiri di komputer masing-masing; penggunaan lokal tidak membutuhkan akun cloud atau server publik.

## Mulai cepat — Windows 10/11

**Persyaratan:** Windows 64-bit, Python 3.15.x (Python 3.15.2 didukung), dan koneksi internet saat pertama kali memasang dependensi.

1. Buka repository [Oceppppp/ors-studio](https://github.com/Oceppppp/ors-studio).
2. Klik **Code → Download ZIP**, lalu ekstrak file ZIP. Alternatifnya, gunakan Git:

   ~~~cmd
   git clone https://github.com/Oceppppp/ors-studio.git
   cd ors-studio
   ~~~

3. Pastikan Python 3.15 tersedia:

   ~~~cmd
   py -3.15 --version
   ~~~

4. Buka folder ORS, lalu jalankan setup_windows.bat dari File Explorer atau Command Prompt:

   ~~~cmd
   setup_windows.bat
   ~~~

5. Setelah setup selesai, jalankan:

   ~~~cmd
   START_ORS.bat
   ~~~

6. Browser akan membuka ORS secara otomatis. Biarkan jendela terminal tetap terbuka selama aplikasi digunakan. Tekan Ctrl+C pada jendela tersebut untuk menghentikan server.

**Penting:** jangan mengetik setup_windows.bat pada Python Shell yang menampilkan prompt >>>. File .bat harus dijalankan dari File Explorer, Command Prompt, atau PowerShell.

Panduan lengkap, screenshot langkah, dan troubleshooting: [Panduan Menjalankan ORS dari Terminal](docs/QUICK_START_TERMINAL_ID.md).

## Mulai cepat — macOS / Linux

Repository sudah menyediakan run_local.sh. Script akan membuat virtual environment lokal jika belum ada, memasang dependensi aplikasi lokal, lalu menjalankan ORS.

~~~bash
chmod +x run_local.sh
./run_local.sh
~~~

Python 3 dan internet diperlukan saat pemasangan pertama. Lihat [Developer Guide](docs/DEVELOPER_GUIDE.md) untuk detail lingkungan pengembangan.

## Bagaimana cara kerja mode lokal?

- Backend hanya menerima koneksi dari 127.0.0.1 pada komputer yang menjalankan ORS. Ini bukan server publik atau server jaringan lokal.
- Setiap komputer mempunyai workspace dan database lokal masing-masing.
- Di Windows, data disimpan di %LOCALAPPDATA%\ORS-Studio.
- Di macOS/Linux, data disimpan di ~/.ors-studio secara default.
- Setelah dependensi terpasang, analisis dapat dijalankan tanpa login cloud.

Untuk memberikan ORS kepada teman, bagikan link repository ini: https://github.com/Oceppppp/ors-studio. Teman Anda mengunduh source yang sama, lalu menjalankan langkah instalasi pada komputer mereka sendiri.

## Fitur aplikasi

- 29 module keys untuk Operations Research, Production/Operations Management, dan Quantitative Methods.
- Import CSV dan XLSX, pemilihan worksheet, preview, validasi, dan column mapping.
- Single analysis dan batch processing lokal.
- Perbandingan forecasting dengan MAD, MSE, RMSE, MAPE, serta pemilihan metode berdasarkan holdout MAD.
- Grafik, riwayat analisis, dan ekspor Excel, CSV, serta PDF.
- Kode Public Web terpisah dengan Guest/Account Mode dan PostgreSQL (opsional; tidak diperlukan untuk menjalankan aplikasi lokal).

Jumlah 29 module keys bukan berarti seluruh submodel lanjutan di setiap versi POM-QM sudah direplikasi. Periksa [Module Implementation Scope](docs/MODULE_IMPLEMENTATION_SCOPE.md) untuk cakupan dan batasan setiap solver.

## Dokumentasi

- [Panduan Menjalankan ORS dari Terminal](docs/QUICK_START_TERMINAL_ID.md)
- [Panduan Python 3.15 dan Troubleshooting](docs/PYTHON_315_SETUP.md)
- [Panduan Pengguna](docs/PANDUAN_PENGGUNA.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Katalog 29 Modul](docs/MODULE_CATALOG.md)
- [Cakupan Implementasi Solver](docs/MODULE_IMPLEMENTATION_SCOPE.md)
- [Deployment Netlify + Railway (opsional)](docs/RAILWAY_NETLIFY_DEPLOYMENT.md)

## Pengingat privasi

Mode lokal menyimpan data di komputer masing-masing. Saat melaporkan bug ke GitHub, jangan mengunggah password, session cookie, dataset pribadi, data perusahaan rahasia, atau informasi pribadi.
