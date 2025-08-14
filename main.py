import os
import subprocess
import requests
import time
from datetime import datetime

DEFECTDOJO_URL = "https://defectdojo.example.com/api/v2"
API_KEY = "TOKEN_API_DEFECTDOJO"
HEADERS = {"Authorization": f"Token {API_KEY}"}
PRODUCT_NAME = input("Masukkan nama Product di DefectDojo: ").strip()
TARGET_URL = input("Masukkan target URL untuk scan Nuclei: ").strip()

# Nuclei output JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = "/your/output/directory"
os.makedirs(output_dir, exist_ok=True)
json_file = os.path.join(output_dir, f"nuclei_{timestamp}.json")

print(f"[+] Memulai scan Nuclei terhadap {TARGET_URL} ...")
start_time = time.time()
try:
    subprocess.run(
        ["nuclei", "-u", TARGET_URL, "-json-export", json_file], check=True, timeout=600
    )
except subprocess.TimeoutExpired:
    print("[!] Scan dihentikan karena melebihi batas waktu 10 menit.")
    exit(1)
except subprocess.CalledProcessError:
    print("[!] Terjadi kesalahan saat menjalankan Nuclei.")
    exit(1)

elapsed = time.time() - start_time
print(f"[+] Scan selesai dalam {elapsed:.2f} detik, hasil disimpan di {json_file}")

if not os.path.exists(json_file):
    print("[!] File hasil scan tidak ditemukan. Proses upload dibatalkan.")
    exit(1)


# Cek atau buat Product
def get_or_create_product(name):

    r = requests.get(f"{DEFECTDOJO_URL}/products/?name={name}", headers=HEADERS)
    if r.status_code == 200 and r.json()["count"] > 0:
        return r.json()["results"][0]["id"]

    r_type = requests.get(f"{DEFECTDOJO_URL}/product_types/", headers=HEADERS)
    r_type.raise_for_status()
    prod_type_id = r_type.json()["results"][0]["id"]

    payload = {
        "name": name,
        "prod_type": prod_type_id,
        "description": f"Product {name} dibuat otomatis via API",
    }
    r = requests.post(
        f"{DEFECTDOJO_URL}/products/",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
    )
    r.raise_for_status()
    return r.json()["id"]


product_id = get_or_create_product(PRODUCT_NAME)
print(f"[+] Product ID: {product_id}")

# Engagement
engagement_payload = {
    "name": f"Nuclei Scan {timestamp}",
    "product": product_id,
    "status": "In Progress",
    "target_start": datetime.now().strftime("%Y-%m-%d"),
    "target_end": datetime.now().strftime("%Y-%m-%d"),
    "engagement_type": "CI/CD",
}
r = requests.post(
    f"{DEFECTDOJO_URL}/engagements/",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=engagement_payload,
)
r.raise_for_status()
engagement_id = r.json()["id"]
print(f"[+] Engagement ID: {engagement_id}")

# Upload Scan
with open(json_file, "rb") as f:
    files = {"file": f}
    data = {
        "scan_type": "Nuclei Scan",
        "engagement": engagement_id,
        "minimum_severity": "Info",
        "active": "true",
        "verified": "true",
        "scan_date": datetime.now().strftime("%Y-%m-%d"),
    }
    r = requests.post(
        f"{DEFECTDOJO_URL}/import-scan/", headers=HEADERS, files=files, data=data
    )
    r.raise_for_status()

print("[+] Hasil scan berhasil diunggah ke DefectDojo")
