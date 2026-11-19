# Panduan Menjalankan ORS Studio dari Terminal (Windows)

Panduan ini untuk pengguna yang ingin menjalankan ORS Studio di komputer sendiri. Anda tidak perlu membuat akun Railway, Netlify, Render, PostgreSQL, atau Redis untuk memakai mode Desktop/local.

## Ringkasan

1. Unduh source ORS dari GitHub.
2. Pasang Python 3.15.x 64-bit.
3. Jalankan setup_windows.bat satu kali.
4. Jalankan START_ORS.bat setiap kali ingin memakai ORS.
5. Browser membuka aplikasi lokal di komputer Anda.

Repository resmi: https://github.com/Oceppppp/ors-studio

## A. Persiapan

Yang diperlukan:
- Windows 10 atau Windows 11, 64-bit.
- Python 3.15.x 64-bit. Versi Python 3.15.2 telah menjadi target setup Windows ORS.
- Internet saat pertama kali memasang library Python.
- Ruang disk untuk source, virtual environment, dan library analisis.

Unduh Python dari situs resmi: https://www.python.org/downloads/windows/

Saat instalasi Python:
- Pastikan Python Launcher terpasang.
- Centang opsi Add Python to PATH jika ditampilkan.
- Gunakan installer 64-bit.

Setelah instalasi, buka Command Prompt dan periksa:

~~~cmd
py -3.15 --version
~~~

Hasil yang diharapkan adalah Python 3.15.x. Jika perintah tidak dikenali, tutup lalu buka kembali Command Prompt. Jika tetap gagal, jalankan Python Installer lagi dan pastikan Python Launcher ikut dipasang.

## B. Unduh source ORS dari GitHub

### Cara 1 — Download ZIP (paling mudah)

1. Buka https://github.com/Oceppppp/ors-studio
2. Klik tombol **Code**.
3. Pilih **Download ZIP**.
4. Setelah selesai, klik kanan ZIP dan pilih **Extract All**.
5. Simpan folder hasil ekstrak di lokasi sederhana, misalnya:

~~~text
C:\Users\NamaAnda\Documents\ors-studio
~~~

Jangan menjalankan file langsung dari dalam ZIP. Ekstrak terlebih dahulu.

### Cara 2 — Git clone

Jika Git sudah terpasang, buka Command Prompt dan jalankan:

~~~cmd
git clone https://github.com/Oceppppp/ors-studio.git
cd ors-studio
~~~

## C. Jalankan setup pertama kali

Cara paling mudah:
1. Buka folder ors-studio di File Explorer.
2. Temukan file setup_windows.bat.
3. Klik dua kali file tersebut.
4. Tunggu sampai proses instalasi selesai.

Atau jalankan melalui Command Prompt:

1. Buka folder ors-studio di File Explorer.
2. Klik address bar (bagian atas yang menampilkan lokasi folder).
3. Ketik cmd lalu tekan Enter.
4. Pada Command Prompt yang terbuka, jalankan:

~~~cmd
setup_windows.bat
~~~

Setup akan:
- Mencari Python 3.15.
- Membuat folder virtual environment .venv.
- Memasang dependensi Python yang diperlukan.
- Memaksa penggunaan binary wheels untuk menghindari kompilasi native library yang tidak perlu.
- Memeriksa apakah FastAPI, NumPy, SciPy, Pandas, OpenPyXL, dan library lainnya dapat di-import.

Tunggu sampai muncul pesan:

~~~text
Setup complete. Start ORS Studio using START_ORS.bat.
~~~

Jika muncul ERROR, jangan tutup jendela sebelum menyalin pesan error lengkapnya.

## D. Jalankan ORS

Setiap kali ingin menggunakan ORS:

1. Buka folder ors-studio.
2. Klik dua kali START_ORS.bat.

Atau dari Command Prompt pada folder project:

~~~cmd
START_ORS.bat
~~~

Script akan menjalankan backend lokal dan membuka browser secara otomatis. Alamat biasanya berupa http://127.0.0.1:<port>.

**Biarkan jendela terminal tetap terbuka selama ORS digunakan.** Jika jendela ditutup atau Anda menekan Ctrl+C, server lokal berhenti.

## E. Cara teman Anda menggunakan ORS

Bagikan repository resmi ini kepada teman Anda:

https://github.com/Oceppppp/ors-studio

Setiap teman perlu:
1. Mengunduh source sendiri dari GitHub.
2. Memasang Python 3.15.x 64-bit.
3. Menjalankan setup_windows.bat.
4. Menjalankan START_ORS.bat.

Mereka tidak memakai server atau database komputer Anda. Setiap komputer mempunyai workspace sendiri. Perubahan data pada komputer Anda tidak otomatis muncul di komputer teman.

## F. Lokasi penyimpanan data

Di Windows, database dan workspace lokal disimpan pada:

~~~text
%LOCALAPPDATA%\ORS-Studio
~~~

Folder tersebut berada di profil Windows pengguna masing-masing. Jangan menghapus folder tersebut jika ingin mempertahankan proyek dan hasil analisis lokal.

## G. Troubleshooting

### Muncul NameError: setup_windows is not defined

Anda mengetik file BAT pada Python Shell yang menampilkan prompt >>>.

Solusi:
1. Ketik exit() lalu tekan Enter.
2. Jalankan setup_windows.bat melalui File Explorer atau Command Prompt.

### Python 3.15 tidak ditemukan

Periksa:

~~~cmd
py -0p
py -3.15 --version
~~~

Pastikan Python 3.15.x 64-bit dan Python Launcher terpasang.

### Setup gagal memasang library

- Pastikan internet stabil.
- Pastikan Windows 64-bit.
- Salin seluruh pesan error dari Command Prompt.
- Jangan menghapus opsi --only-binary dari setup script tanpa memahami kebutuhan wheel NumPy/SciPy.

### Browser tidak terbuka

- Pastikan jendela terminal masih berjalan.
- Salin alamat Local app yang tercetak pada terminal.
- Tempel alamat tersebut ke browser pada komputer yang sama.

### Port sedang digunakan

Tutup proses ORS lama yang masih berjalan atau tekan Ctrl+C pada jendela terminal lama. Jalankan START_ORS.bat kembali.

### Ingin menghentikan ORS

Klik jendela terminal yang menjalankan ORS, lalu tekan Ctrl+C.

## H. Batasan mode terminal/lokal

- Mode ini hanya untuk komputer yang menjalankan ORS.
- Backend mengikat ke 127.0.0.1, bukan IP publik.
- Jangan mengubah host menjadi 0.0.0.0 untuk membagikan aplikasi tanpa autentikasi dan audit keamanan.
- Link localhost/127.0.0.1 tidak dapat dipakai teman dari komputer lain.
- Untuk satu website publik yang dipakai bersama oleh banyak orang, gunakan deployment Web terpisah sesuai panduan Netlify + Railway. Itu bukan syarat untuk menjalankan mode lokal.

## I. Bantuan

Jika masih gagal:
1. Catat Windows version dan hasil py -3.15 --version.
2. Salin pesan error lengkap.
3. Kirim hanya log yang sudah disamarkan; jangan kirim password, cookie, file dataset pribadi, atau data perusahaan.
4. Laporkan masalah pada https://github.com/Oceppppp/ors-studio/issues.
