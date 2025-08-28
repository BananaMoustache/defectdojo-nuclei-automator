#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import argparse
import requests

from .config import DEFECTDOJO_URL, API_KEY, DEFAULT_OUT_DIR, SCAN_PROFILES
from .utils import (
    now_str,
    slugify,
    split_by_host_to_json_arrays,
    count_findings_from_file,
    canonical_host_from_any,
)
from .nuclei_runner import nuclei_list, nuclei_single
from .dojo_client import (
    dd_ensure_product,
    dd_create_engagement,
    dd_import_scan,
    extract_findings_count,
)

def product_name_from_target(target: str) -> str:
    return canonical_host_from_any(target)

def handle_import_for_hostfile(dd_url: str, token: str, host: str, host_file: str):
    product_name = host
    prod = dd_ensure_product(dd_url, token, product_name)
    eng = dd_create_engagement(dd_url, token, prod.get("id"), name=f"Scan {now_str()}")
    res = dd_import_scan(dd_url, token, host_file, eng.get("id"))
    findings = extract_findings_count(res)
    if findings is None or findings == 0:
        findings = count_findings_from_file(host_file) or "?"
    print(f"[OK] Upload '{product_name}' (findings: {findings})")


def _profile_params(profile_name: str):
    p = SCAN_PROFILES.get(profile_name or "default", SCAN_PROFILES["default"])
    return (
        p.get("include_tags"),
        p.get("exclude_tags"),
        p.get("exclude_templates"),
    )

def run_mode_list(args: argparse.Namespace):
    dd_url = args.dd_url or DEFECTDOJO_URL
    token = args.dd_token or API_KEY
    include_tags, exclude_tags, exclude_templates = _profile_params(args.scan_profile)
    if not token:
        raise SystemExit("[!] DD token is required. Use --dd-token or ENV DD_TOKEN.")

    out_dir = args.out_dir or str(DEFAULT_OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    tmp_json = nuclei_list(
        args.targets,
        severity=args.severity,
        include_tags=include_tags,
        exclude_tags=exclude_tags,
        exclude_templates=exclude_templates,
        rate_limit=args.rate_limit,
        concurrency=args.concurrency,
    )

    host_files = split_by_host_to_json_arrays(tmp_json, out_dir)

    if args.save_json:
        ts = now_str()
        final_json = os.path.join(out_dir, f"nuclei_list_{ts}.json")
        shutil.copy2(tmp_json, final_json)
        print(f"[+] Combined JSON copied: {final_json}")
    try:
        if not args.save_json:
            os.remove(tmp_json)
    except Exception:
        pass

    success, total = 0, len(host_files)
    for host, fp in host_files.items():
        try:
            handle_import_for_hostfile(dd_url, token, host, fp)
            success += 1
        except requests.HTTPError as e:
            print(
                f"[ERR] {host}: HTTP {e.response.status_code} -> {e.response.text[:500]}"
            )
        except Exception as e:
            print(f"[ERR] {host}: {e}")
        finally:
            if not args.save_json:
                try:
                    os.remove(fp)
                except Exception:
                    pass
    print(f"[=] Done: {success}/{total} hosts uploaded.")

def run_mode_single(args: argparse.Namespace):
    dd_url = args.dd_url or DEFECTDOJO_URL
    token = args.dd_token or API_KEY
    include_tags, exclude_tags, exclude_templates = _profile_params(args.scan_profile)
    if not token:
        raise SystemExit("[!] DD token is required. Use --dd-token or ENV DD_TOKEN.")

    target = args.target
    if not target:
        raise SystemExit("[!] Single mode requires --target.")

    out_dir = args.out_dir or str(DEFAULT_OUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n[+] Starting single-target scan: {target}")
    try:
        tmp_json = nuclei_single(
            target,
            severity=args.severity,
            include_tags=include_tags,            
            exclude_tags=exclude_tags,            
            exclude_templates=exclude_templates,
            rate_limit=args.rate_limit,
            concurrency=args.concurrency,
        )

        host = product_name_from_target(target)
        safe_host = slugify(host)

        product = dd_ensure_product(dd_url, token, host)
        eng = dd_create_engagement(
            dd_url, token, product.get("id"), name=f"Scan {now_str()}"
        )
        res = dd_import_scan(dd_url, token, tmp_json, eng.get("id"))
        findings = extract_findings_count(res)
        if findings is None or findings == 0:
            findings = count_findings_from_file(tmp_json) or "?"
        print(f"[OK] Upload '{host}' (findings: {findings})")

        if args.save_json:
            ts = now_str()
            final_json = os.path.join(out_dir, f"nuclei_{safe_host}_{ts}.json")
            shutil.copy2(tmp_json, final_json)
            print(f"[+] JSON copied: {final_json}")
        else:
            try:
                os.remove(tmp_json)
            except Exception:
                pass

    except requests.HTTPError as e:
        print(f"[ERR] HTTP {e.response.status_code} -> {e.response.text[:500]}")
    except Exception as e:
        print(f"[ERR] {e}")
