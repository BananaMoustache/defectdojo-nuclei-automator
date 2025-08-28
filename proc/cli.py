#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from .config import DEFAULT_OUT_DIR


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Nuclei → DefectDojo Automator (modes: list, single)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--mode",
        choices=["list", "single"],
        required=True,
        help="Mode: 'list' for nuclei -list; 'single' for single target scan.",
    )
    p.add_argument("--targets", help="Path to .txt file of targets (for mode=list).")
    p.add_argument("--target", help="Single target URL (for mode=single).")
    p.add_argument(
        "--dd-url",
        default=os.environ.get("DD_URL"),
        help="DefectDojo API v2 base URL (or ENV DD_URL).",
    )
    p.add_argument(
        "--dd-token",
        default=os.environ.get("DD_TOKEN"),
        help="DefectDojo API Token (or ENV DD_TOKEN).",
    )
    p.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Output directory to save JSON (if --save-json).",
    )
    p.add_argument("--save-json", action="store_true", help="Keep JSON scan files.")
    p.add_argument(
        "-s",
        "--severity",
        help="Nuclei severity filter (e.g. 'info' or 'low,medium,high,critical').",
    )
    p.add_argument(
        "--scan-profile",
        choices=["default", "asm"],
        default="default",
        help="Scan profile: 'asm' utilizing dedicated tags/exclude for ASM, 'default' = full templates.",
    )
    p.add_argument(
        "-rl",
        "--rate-limit",
        type=int,
        help="Limit on requests per second for Nuclei (example: 120).",
    )
    p.add_argument(
        "-c",
        "--concurrency",
        type=int,
        help="Number of worker concurrency for Nuclei (example: 80).",
    )
    p.add_argument(
        "-ut",
        "--update-templates",
        action="store_true",
        help="Run ‘nuclei -ut’ before the scan begins.",
    )
    return p
