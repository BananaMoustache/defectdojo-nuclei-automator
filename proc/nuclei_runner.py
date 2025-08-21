#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import subprocess
import tempfile
import uuid
from typing import Optional


def ensure_nuclei():
    if shutil.which("nuclei") is None:
        raise RuntimeError(
            "Nuclei not found in PATH. Ensure it can be executed as 'nuclei'."
        )


def nuclei_single(
    url: str,
    json_export_path: Optional[str] = None,
    timeout_sec: int = 1800,
    severity: Optional[str] = None,
) -> str:
    """
    Run nuclei -u <url> [-severity <sev>] -json-export <path>
    severity example: "info" or "low,medium,high,critical"
    """
    ensure_nuclei()
    if json_export_path is None:
        json_export_path = (
            f"{tempfile.gettempdir()}/nuclei_single_{uuid.uuid4().hex}.json"
        )
    cmd = ["nuclei", "-u", url, "-json-export", json_export_path]
    if severity:
        cmd.extend(["-severity", severity])  # equivalent to -s info intent
    print(f"[+] Nuclei single: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, timeout=timeout_sec)
    return json_export_path


def nuclei_list(
    list_file: str,
    json_export_path: Optional[str] = None,
    timeout_sec: int = 3600,
    severity: Optional[str] = None,
) -> str:
    """
    Run nuclei -list <file> [-severity <sev>] -json-export <path>
    """
    ensure_nuclei()
    if json_export_path is None:
        json_export_path = (
            f"{tempfile.gettempdir()}/nuclei_list_{uuid.uuid4().hex}.json"
        )
    cmd = ["nuclei", "-list", list_file, "-json-export", json_export_path]
    if severity:
        cmd.extend(["-severity", severity])
    print(f"[+] Nuclei list: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, timeout=timeout_sec)
    return json_export_path
