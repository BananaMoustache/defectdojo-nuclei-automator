import os
import subprocess
import requests
import time
import tempfile
from datetime import datetime

DEFECTDOJO_URL = "https://defectdojo.example.com/api/v2"
API_KEY = "TOKEN_API_DEFECTDOJO"
HEADERS = {"Authorization": f"Token {API_KEY}"}
PRODUCT_NAME = input("Enter the Product name in DefectDojo: ").strip()
TARGET_URL = input("Enter the target URL for Nuclei scan: ").strip()

# Nuclei output JSON
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

save_choice = input("Save JSON results to file? (y/n): ").strip().lower()
temp_file_created = False
if save_choice in ("y", "yes"):
    output_dir = "/your/output/directory"
    os.makedirs(output_dir, exist_ok=True)
    json_file = os.path.join(output_dir, f"nuclei_{timestamp}.json")
else:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    json_file = tmp.name
    tmp.close()
    temp_file_created = True

try:
    print(f"[+] Starting Nuclei scan of {TARGET_URL} ...")
    start_time = time.time()
    try:
        subprocess.run(
            ["nuclei", "-u", TARGET_URL, "-json-export", json_file],
            check=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("[!] Scan stopped because it exceeded the 10-minute time limit.")
        raise SystemExit(1)
    except subprocess.CalledProcessError:
        print(
            "[!] An error occurred while running Nuclei. Please check if Nuclei is installed and configured correctly."
        )
        raise SystemExit(1)

    elapsed = time.time() - start_time
    print(f"[+] Scan completed in {elapsed:.2f} seconds, results saved in {json_file}")

    if not os.path.exists(json_file):
        print("[!] The scanned file was not found. The upload process was canceled.")
        raise SystemExit(1)

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
            "description": f"Product {name} created by automated script",
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

    print("[+] The scan results were successfully uploaded to DefectDojo.")

finally:
    if temp_file_created and os.path.exists(json_file):
        try:
            os.remove(json_file)
            print("[+] Temporary file successfully deleted.")
        except Exception:
            print(f"[!] Failed to delete temporary file: {json_file}")
