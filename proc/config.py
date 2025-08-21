#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Project base dir (folder containing main.py and proc/)
BASE_DIR = Path(__file__).resolve().parents[1]

# Default outputs folder
DEFAULT_OUT_DIR = BASE_DIR / "outputs"
DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)

# DefectDojo configuration (env-overridable)
DEFECTDOJO_URL = os.environ.get("DD_URL", "http://127.0.0.1:42003/api/v2")
API_KEY = os.environ.get("DD_TOKEN", "")

# Product Type config
PROD_TYPE_NAME = os.environ.get("DD_PROD_TYPE_NAME", "Research and Development")
PROD_TYPE_ID_ENV = os.environ.get("DD_PROD_TYPE_ID")  # optional int


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
