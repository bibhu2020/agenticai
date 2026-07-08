"""GitHub client for pushing generated audio to the shared bibhu2020/media repo.

Mirrors src/fifa/backend/utils/github_client.py's approach: keeps large/volatile
binary data out of the main agenticai repo's git history.
"""
from __future__ import annotations
import base64
import os

import requests

MEDIA_REPO = "bibhu2020/media"
BRANCH = "main"
AUDIO_PREFIX = "news/audio"


def _get_headers(write: bool = False) -> dict:
    token = os.environ.get("GH_MEDIA_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    if write:
        headers["Content-Type"] = "application/json"
    return headers


def push_audio_bytes(audio_bytes: bytes, remote_path: str) -> str:
    """
    Push audio bytes to bibhu2020/media at news/audio/<remote_path>, creating or
    updating the file. Returns the raw.githubusercontent.com URL for the file.
    """
    token = os.environ.get("GH_MEDIA_TOKEN", "")
    if not token:
        raise RuntimeError("GH_MEDIA_TOKEN is not set")

    full_path = f"{AUDIO_PREFIX}/{remote_path}"
    api_url = f"https://api.github.com/repos/{MEDIA_REPO}/contents/{full_path}"
    headers = _get_headers(write=True)

    get_resp = requests.get(api_url, headers=headers, timeout=10)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    payload: dict = {
        "message": f"chore: update {full_path}",
        "content": base64.b64encode(audio_bytes).decode(),
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(api_url, headers=headers, json=payload, timeout=30)
    put_resp.raise_for_status()

    return f"https://raw.githubusercontent.com/{MEDIA_REPO}/{BRANCH}/{full_path}"
