"""GitHub client for reading/writing the FIFA Excel file in bibhu2020/media."""
from __future__ import annotations
import os
import base64
import requests

MEDIA_REPO = "bibhu2020/media"
BRANCH = "main"
EXCEL_PATH = "fifa/fifa_data.xlsx"


def _get_headers(write: bool = False) -> dict:
    token = os.environ.get("GH_MEDIA_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    if write:
        headers["Content-Type"] = "application/json"
    return headers


def download_excel() -> bytes | None:
    """Download fifa_data.xlsx from GitHub as raw bytes."""
    token = os.environ.get("GH_MEDIA_TOKEN", "")
    raw_url = f"https://raw.githubusercontent.com/{MEDIA_REPO}/{BRANCH}/{EXCEL_PATH}"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    resp = requests.get(raw_url, headers=headers, timeout=15)
    if resp.status_code == 200:
        return resp.content
    return None


def push_excel(local_path: str) -> bool:
    """Push local Excel file to GitHub, creating or updating the file."""
    token = os.environ.get("GH_MEDIA_TOKEN", "")
    if not token:
        raise RuntimeError("GH_MEDIA_TOKEN is not set")

    with open(local_path, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode()

    api_url = f"https://api.github.com/repos/{MEDIA_REPO}/contents/{EXCEL_PATH}"
    headers = _get_headers(write=True)

    # Get current file SHA (required for updates)
    get_resp = requests.get(api_url, headers=headers, timeout=10)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    payload: dict = {
        "message": "chore: update FIFA World Cup 2026 data",
        "content": encoded,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(api_url, headers=headers, json=payload, timeout=20)
    return put_resp.status_code in (200, 201)
