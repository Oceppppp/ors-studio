# Panduan Pengguna — ORS Studio v0.4.0

ORS memiliki dua cara penggunaan: Web publik (Guest atau akun) dan Desktop lokal.

## A. Menggunakan Public Web

Setelah Web Edition benar-benar dideploy, buka URL publik yang diumumkan oleh pengelola ORS.

1. Pilih **Continue as guest** untuk mencoba tanpa mendaftar, atau pilih **Create account** untuk membuat akun.
2. Untuk akun, gunakan email yang dapat diakses dan password unik minimal 12 karakter yang berisi huruf dan angka. Pada beta ini email belum diverifikasi dan password reset belum tersedia.
3. Buat project atau gunakan workspace default.
4. Buka **Data Center**, upload CSV/XLSX, pilih worksheet bila workbook memiliki beberapa sheet, lalu import.
5. Buka **Analysis Modules**, pilih salah satu dari 29 modul, atur parameter, lalu hubungkan kolom dataset bila diperlukan.
6. Pilih **Run analysis** untuk satu perhitungan atau **Add to batch** kemudian jalankan batch untuk beberapa pekerjaan independen.
7. Pantau status pada Batch Processing atau Analysis History.
8. Buka hasil dan ekspor ke Excel, CSV, atau PDF.
9. Guest dapat memilih **Save workspace** untuk mengubah guest menjadi akun dan mempertahankan project yang sudah dibuat.

### Guest limits

Guest session berlaku 24 jam dan memiliki batas upload, jumlah dataset, project, row, batch, serta jumlah analisis. Data guest akan dibersihkan setelah masa berlaku habis.

### Privasi

Project dan dataset pada Web bersifat privat untuk akun/guest pemiliknya. Jangan masukkan data rahasia perusahaan atau data pribadi sensitif pada public beta sebelum membaca kebijakan privasi dan ketentuan layanan yang diterbitkan pengelola.

## B. Menggunakan Desktop/local

Desktop edition berjalan pada komputer sendiri dan tidak membutuhkan akun Web.

### Source mode Windows

1. Instal Python 3.15.x 64-bit.
2. Ekstrak source Desktop.
3. Jalankan `setup_windows.bat` dari File Explorer.
4. Jalankan `START_ORS.bat` setelah setup berhasil.
5. Browser membuka alamat loopback lokal. Jangan mengubah bind address menjadi alamat publik/LAN.

### Installer Windows

Installer mandiri akan tersedia pada GitHub Releases setelah workflow Windows berhasil dan clean-machine test selesai. Jangan mengunduh installer dari sumber selain repository ORS resmi.

## C. Memahami hasil

Setiap module hanya mendukung varian yang tertulis di `MODULE_IMPLEMENTATION_SCOPE.md`. Periksa asumsi, satuan, batas metode, dan status solver sebelum memakai hasil untuk keputusan nyata. Ketersediaan 29 module keys tidak berarti seluruh submodel setiap versi POM-QM telah direplikasi.

## D. Dukungan dan pelaporan masalah

Laporkan bug melalui tab **Issues** pada repository GitHub. Sertakan langkah reproduksi, versi ORS, OS, dan contoh data yang sudah disamarkan. Jangan unggah data sensitif, password, session cookie, atau file perusahaan yang rahasia.
