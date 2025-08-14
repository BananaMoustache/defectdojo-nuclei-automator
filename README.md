### DefectDojo Nuclei Automator

**Skrip Python untuk otomatisasi alur kerja keamanan aplikasi** — menjalankan pemindaian kerentanan menggunakan **[Nuclei](https://github.com/projectdiscovery/nuclei)** dan langsung mengunggah hasilnya ke **[DefectDojo](https://github.com/DefectDojo/django-DefectDojo)** untuk pelacakan serta manajemen.

<div align="center">
  <img src="https://projectdiscovery.io/_next/image?url=https%3A%2F%2Fprojectdiscovery.ghost.io%2Fcontent%2Fimages%2F2024%2F01%2FBlog---v2.5.png&w=828&q=75" width="150" alt="Nuclei Logo">
  <br>
  <img src="https://cloud.defectdojo.com/static/daas/images/defectdojologo.png" width="150" alt="DefectDojo Logo">
</div>


- Scan & laporkan ke DefectDojo dengan satu perintah.
- Cek otomatis apakah Product sudah ada, jika belum skrip membuatnya.
- Hasil scan disimpan dalam Engagement baru dengan nama unik berdasarkan waktu.
- Input langsung dari pengguna untuk Product name & target URL saat eksekusi.

---

## Workflow

```text
 ┌─────────────────┐
 │  Input Pengguna │
 │ (Target & Nama) │
 └────────┬────────┘
          ▼
  ┌──────────────┐
  │  Nuclei Scan │
  │ (Kerentanan) │
  └───────┬──────┘
          ▼
 ┌──────────────────┐
 │  DefectDojo API  │
 │ (Produk & Eng.)  │
 └────────┬─────────┘
          ▼
 ┌───────────────────┐
 │  Laporan Dibuat   │
 │ (Temuan diimpor)  │
 └───────────────────┘

```

---

## Prasyarat
> Python ≥ 3.6 , Git, Nuclei (pastikan dapat diakses dari terminal)

---

## Instalasi & Konfigurasi

- Clone Repositori
```text
git clone https://github.com/BananaMoustache/defectdojo-nuclei-automator
cd defectdojo-nuclei-automator
```

- Konfigurasi Variabel
Edit main.py:
```text
# URL instance DefectDojo (akhiri dengan /api/v2)
DEFECTDOJO_URL = "https://defectdojo.example.com/api/v2"

# Token API DefectDojo
API_KEY = "TOKEN_API_DEFECTDOJO"

# Direktori penyimpanan hasil scan sementara (opsional)
output_dir = "scan_results"
```

## Run Script
```text
python main.py
```

Skrip akan meminta:
- Nama Product di DefectDojo
- URL Target untuk dipindai oleh Nuclei
