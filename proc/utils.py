#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import os
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, List, Iterable


def show_banner(title_line: str = "Nuclei2Dojo", ascii_only: bool = False) -> None:
    art = r"""
   _  __         __    _ ___  ___         _    
  / |/ /_ ______/ /__ (_)_  |/ _ \___    (_)__ 
 /    / // / __/ / -_) / __// // / _ \  / / _ \
/_/|_/\_,_/\__/_/\__/_/____/____/\___/_/ /\___/
                                    |___/      
"""
    sep = ("─" * 76) if not ascii_only else ("-" * 76)
    print("\n" + art.rstrip())
    print(sep)
    print(f"{title_line}")
    print(sep + "\n")


def now_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9\-_.]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "unknown"


def _strip_port_from_netloc(netloc: str) -> str:
    if not netloc:
        return ""
    netloc = netloc.strip()
    m = re.match(r"^\[(?P<h>.+)\](?::\d+)?$", netloc)  # [IPv6]:port?
    if m:
        return m.group("h")
    return re.sub(r":\d+$", "", netloc)


def canonical_host_from_any(s: str) -> str:
    if not s:
        return "unknown"
    s = str(s).strip()
    if "://" in s:
        p = urlparse(s)
        base = p.netloc or p.path or s
    else:
        p = urlparse("dummy://" + s)
        base = p.netloc or p.path or s
    base = base.split("/")[0]
    host = _strip_port_from_netloc(base)
    host = host or s
    return host.lower()


def read_lines(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f if ln.strip()]


def iter_nuclei_records(path: str) -> Iterable[dict]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read().strip()
    if not data:
        return
    # try full JSON (dict or list)
    try:
        obj = json.loads(data)
        if isinstance(obj, dict):
            yield obj
            return
        elif isinstance(obj, list):
            for rec in obj:
                if isinstance(rec, dict):
                    yield rec
            return
    except json.JSONDecodeError:
        pass
    # fallback: jsonl lines or mixed
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            yield obj
        elif isinstance(obj, list):
            for rec in obj:
                if isinstance(rec, dict):
                    yield rec


def count_findings_from_file(json_path: str) -> int:
    try:
        with open(json_path, "r", encoding="utf-8", errors="ignore") as f:
            data = f.read().strip()
        if not data:
            return 0
        try:
            obj = json.loads(data)
            if isinstance(obj, list):
                return len([x for x in obj if isinstance(x, dict)])
            if isinstance(obj, dict):
                return 1
        except json.JSONDecodeError:
            pass
        return sum(1 for _ in iter_nuclei_records(json_path))
    except Exception:
        return 0


def extract_host_from_record(rec: dict) -> str:
    for key in ("host", "ip", "url", "matched-at"):
        val = rec.get(key)
        if val:
            h = canonical_host_from_any(val)
            if h and h != "unknown":
                return h
    req = rec.get("request")
    if isinstance(req, dict):
        val = req.get("url")
        if val:
            h = canonical_host_from_any(val)
            if h and h != "unknown":
                return h
    return "unknown"


def split_by_host_to_json_arrays(src_json_path: str, out_dir: str) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    buckets: Dict[str, List[dict]] = {}
    total = 0
    for rec in iter_nuclei_records(src_json_path):
        total += 1
        if not isinstance(rec, dict):
            continue
        host = extract_host_from_record(rec)
        buckets.setdefault(host, []).append(rec)
    print(f"[+] Findings: {total} | Unique hosts: {len(buckets)}")
    host_files: Dict[str, str] = {}
    ts = now_str()
    for host, records in buckets.items():
        safe_host = slugify(host)
        out_path = os.path.join(out_dir, f"nuclei_{safe_host}_{ts}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        host_files[host] = out_path
        print(f"    - {host}: {len(records)} → {out_path}")
    return host_files
