DefectDojo Nuclei Automator
Skrip Python ini mengotomatiskan seluruh alur kerja keamanan: menjalankan pemindaian kerentanan menggunakan Nuclei pada target yang ditentukan, kemudian secara otomatis mengunggah hasilnya ke dalam DefectDojo untuk pelacakan dan manajemen.

Fitur Utama
Otomatisasi Penuh: Menjalankan scan Nuclei dan melaporkan ke DefectDojo dengan satu perintah.

Manajemen Produk Cerdas: Secara otomatis memeriksa apakah sebuah Product sudah ada di DefectDojo. Jika belum, skrip akan membuatnya.

Terstruktur: Setiap hasil scan disimpan dalam Engagement baru yang diberi nama unik berdasarkan waktu, sehingga riwayat pemindaian tetap rapi.

Interaktif: Meminta input dari pengguna untuk menentukan nama produk dan target URL saat skrip dijalankan.

Prasyarat
Sebelum menjalankan skrip ini, pastikan Anda sudah menginstal perangkat lunak berikut di sistem Anda:

Python 3.6+

Git

Nuclei: Pastikan Nuclei sudah terpasang dan bisa diakses dari terminal Anda.

⚙ Instalasi & Konfigurasi
Ikuti langkah-langkah ini untuk menyiapkan proyek di komputer lokal Anda.

1. Clone Repositori

Gunakan Git untuk menyalin repositori ini ke komputer Anda:

Bash

git clone https://github.com/USERNAME_ANDA/NAMA_REPOSITORI_ANDA.git
cd NAMA_REPOSITORI_ANDA
2. Instal Dependensi

Skrip ini memerlukan pustaka requests. Instal menggunakan pip:

Bash

pip install requests
Disarankan untuk membuat dan menggunakan lingkungan virtual (virtual environment) Python.

3. Konfigurasi Variabel

Ubah baris-baris berikut di dalam file main.py dengan informasi akun DefectDojo Anda:

Python

# Ganti dengan URL instance DefectDojo Anda (diakhiri dengan /api/v2)
DEFECTDOJO_URL = "https://defectdojo.example.com/api/v2"

# Ganti dengan Token API Anda dari DefectDojo
API_KEY = "TOKEN_API_DEFECTDOJO"

# Ganti direktori default untuk menyimpan hasil scan 
output_dir = "/your/output/directory"

▶ Cara Menjalankan Skrip
Setelah konfigurasi selesai, jalankan skrip dari terminal dengan perintah berikut:

Bash

python main.py
Skrip kemudian akan meminta Anda untuk memasukkan:

Nama Product di DefectDojo.

URL target yang akan dipindai oleh Nuclei.

Skrip akan menampilkan status setiap langkah proses langsung di terminal Anda, mulai dari pemindaian hingga pengunggahan berhasil.

