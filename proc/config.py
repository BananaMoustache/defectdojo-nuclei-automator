#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = BASE_DIR / "outputs"
DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)

DEFECTDOJO_URL = os.environ.get("DD_URL", "http://127.0.0.1:42003/api/v2")
API_KEY = os.environ.get("DD_TOKEN", "")

PROD_TYPE_NAME = os.environ.get("DD_PROD_TYPE_NAME", "Research and Development")
PROD_TYPE_ID_ENV = os.environ.get("DD_PROD_TYPE_ID")

ASM_INCLUDE_TAGS = (
    "exposure,misconfig,panel,default-login,tech,fingerprint,cve,takeover,web"
)
ASM_EXCLUDE_TAGS = "fuzz,dos,bruteforce,network"
ASM_EXCLUDE_TEMPLATES = ["http/fuzzing/", "network/", "dns/"]

SCAN_PROFILES = {
    "default": {
        "include_tags": None,
        "exclude_tags": None,
        "exclude_templates": None,
    },
    "asm": {
        "include_tags": ASM_INCLUDE_TAGS,
        "exclude_tags": ASM_EXCLUDE_TAGS,
        "exclude_templates": ASM_EXCLUDE_TEMPLATES,
    },
}


def HEADERS_JSON(token: str):
    return {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def HEADERS_AUTH(token: str):
    return {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
    }
