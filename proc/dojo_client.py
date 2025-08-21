#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Union

from .config import PROD_TYPE_ID_ENV, PROD_TYPE_NAME, HEADERS_JSON, HEADERS_AUTH
from .utils import utc_today


def _json_or_none(r: requests.Response) -> Any:
    try:
        return r.json()
    except ValueError:
        return None


def _results_from_data(data: Any) -> List[Any]:
    if isinstance(data, dict):
        res = data.get("results")
        if isinstance(res, list):
            return res
        return []
    if isinstance(data, list):
        return data
    return []


def dd_list_product_types(dd_url: str, token: str):
    url = f"{dd_url}/product_types/"
    r = requests.get(url, headers=HEADERS_AUTH(token), timeout=30)
    r.raise_for_status()
    data = _json_or_none(r)
    if data is None:
        print(
            f"[WRN] /product_types/ not JSON. code={r.status_code} body[:200]={r.text[:200]!r}"
        )
        return []
    return _results_from_data(data)


def dd_get_product_type_by_name(dd_url: str, token: str, name: str):
    url = f"{dd_url}/product_types/?name={name}"
    r = requests.get(url, headers=HEADERS_AUTH(token), timeout=30)
    r.raise_for_status()
    data = _json_or_none(r)
    if data is None:
        print(
            f"[WRN] /product_types/?name= not JSON. code={r.status_code} body[:200]={r.text[:200]!r}"
        )
        return None
    for item in _results_from_data(data):
        if isinstance(item, dict) and item.get("name") == name:
            return item
    return None


def dd_create_product_type(dd_url: str, token: str, name: str, description: str = ""):
    url = f"{dd_url}/product_types/"
    payload = {
        "name": name,
        "description": description
        or f"Auto-created {datetime.now().strftime('%Y%m%d_%H%M%S')}",
    }
    r = requests.post(
        url, headers=HEADERS_JSON(token), data=json.dumps(payload), timeout=30
    )
    r.raise_for_status()
    data = _json_or_none(r)
    return data if isinstance(data, dict) else {"id": None, "name": name}


def dd_ensure_product_type(dd_url: str, token: str) -> dict:
    if PROD_TYPE_ID_ENV:
        try:
            return {"id": int(PROD_TYPE_ID_ENV), "name": f"ENV:{PROD_TYPE_ID_ENV}"}
        except ValueError:
            print("[WRN] DD_PROD_TYPE_ID is not an integer; ignored.")
    pt = dd_get_product_type_by_name(dd_url, token, PROD_TYPE_NAME)
    if pt:
        return pt
    try:
        print(f"[INF] Creating Product Type: {PROD_TYPE_NAME}")
        return dd_create_product_type(dd_url, token, PROD_TYPE_NAME)
    except Exception as e:
        print(f"[WRN] Failed to create Product Type: {e}")
        pts = dd_list_product_types(dd_url, token)
        if pts and isinstance(pts, list) and isinstance(pts[0], dict):
            print(
                f"[INF] Using first Product Type: {pts[0].get('name')} (id={pts[0].get('id')})"
            )
            return pts[0]
        raise RuntimeError("No available Product Type.")


def dd_get_product_by_name(dd_url: str, token: str, name: str):
    url = f"{dd_url}/products/?name={name}"
    r = requests.get(url, headers=HEADERS_AUTH(token), timeout=30)
    r.raise_for_status()
    data = _json_or_none(r)
    if data is None:
        print(
            f"[WRN] /products/?name= not JSON. code={r.status_code} body[:200]={r.text[:200]!r}"
        )
        return None
    for item in _results_from_data(data):
        if isinstance(item, dict) and item.get("name") == name:
            return item
    return None


def dd_create_product(
    dd_url: str, token: str, name: str, description: str = ""
) -> dict:
    pt = dd_ensure_product_type(dd_url, token)
    url = f"{dd_url}/products/"
    payload = {
        "name": name,
        "description": description
        or f"Product auto-created {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "prod_type": pt.get("id"),
    }
    r = requests.post(
        url, headers=HEADERS_JSON(token), data=json.dumps(payload), timeout=30
    )
    r.raise_for_status()
    data = _json_or_none(r)
    return data if isinstance(data, dict) else {"id": None, "name": name}


def dd_ensure_product(dd_url: str, token: str, name: str) -> dict:
    prod = dd_get_product_by_name(dd_url, token, name)
    if prod:
        print(f"[INF] Product exists: {name} (id={prod.get('id')})")
        return prod
    print(f"[INF] Creating product: {name}")
    return dd_create_product(dd_url, token, name)


def dd_create_engagement(
    dd_url: str, token: str, product_id: int, name: str, days: int = 1
) -> dict:
    url = f"{dd_url}/engagements/"
    start = datetime.now(timezone.utc).date().isoformat()
    end = (datetime.now(timezone.utc).date() + timedelta(days=days)).isoformat()
    payload = {
        "name": name,
        "product": product_id,
        "target_start": start,
        "target_end": end,
        "status": "In Progress",
        "engagement_type": "CI/CD",
        "deduplication_on_engagement": True,
    }
    r = requests.post(
        url, headers=HEADERS_JSON(token), data=json.dumps(payload), timeout=30
    )
    r.raise_for_status()
    data = _json_or_none(r)
    return data if isinstance(data, dict) else {"id": None}


def dd_import_scan(
    dd_url: str, token: str, file_path: str, engagement_id: int, scan_date: str = None
):
    url = f"{dd_url}/import-scan/"
    if scan_date is None:
        scan_date = utc_today()
    data_form = {
        "engagement": str(engagement_id),
        "scan_type": "Nuclei Scan",
        "active": "true",
        "verified": "false",
        "scan_date": scan_date,
        "minimum_severity": "Info",
        "close_old_findings": "false",
        "push_to_jira": "false",
    }
    with open(file_path, "rb") as fh:
        files = {"file": (os.path.basename(file_path), fh, "application/json")}
        r = requests.post(
            url, headers=HEADERS_AUTH(token), files=files, data=data_form, timeout=120
        )
    r.raise_for_status()
    data = _json_or_none(r)
    if data is None:
        print(
            f"[WRN] /import-scan/ not JSON. code={r.status_code} body[:200]={r.text[:200]!r}"
        )
    return data


def extract_findings_count(api_response: Union[dict, list, None]) -> Union[int, None]:
    if not isinstance(api_response, dict):
        return None
    for key in (
        "findings_count",
        "results_count",
        "count",
        "imported_findings",
        "created",
        "success",
    ):
        val = api_response.get(key)
        if isinstance(val, int) and val >= 0:
            return val
    for k in ("result", "results"):
        if isinstance(api_response.get(k), dict):
            nested = extract_findings_count(api_response.get(k))
            if isinstance(nested, int):
                return nested
    return None
