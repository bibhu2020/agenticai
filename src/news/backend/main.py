"""FastAPI backend for the News PWA."""
from __future__ import annotations
import hmac
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    from utils.data_store import get_news_data
    from utils.github_trigger import trigger_agent_run, get_last_run_status
except ImportError:
    from .utils.data_store import get_news_data
    from .utils.github_trigger import trigger_agent_run, get_last_run_status

app = FastAPI(title="News PWA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AdminRequest(BaseModel):
    passphrase: str


def _check_passphrase(passphrase: str) -> None:
    expected = os.environ.get("NEWS_ADMIN_PASSPHRASE", "")
    if not expected or not hmac.compare_digest(passphrase, expected):
        raise HTTPException(status_code=401, detail="Invalid passphrase")


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/news")
async def get_all_news():
    return JSONResponse(get_news_data())


@app.get("/api/news/{category}")
async def get_category_news(category: str):
    data = get_news_data()
    articles = data.get("categories", {}).get(category)
    if articles is None:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    return JSONResponse({"generated_at": data.get("generated_at"), "articles": articles})


@app.post("/api/admin/trigger")
async def admin_trigger(req: AdminRequest):
    _check_passphrase(req.passphrase)
    try:
        trigger_agent_run()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not trigger workflow: {exc}")
    return {"success": True}


@app.post("/api/admin/status")
async def admin_status(req: AdminRequest):
    _check_passphrase(req.passphrase)
    try:
        return get_last_run_status()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not fetch workflow status: {exc}")


# ── Serve Vue.js SPA ─────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dist = os.path.abspath(os.path.join(current_dir, "../frontend/dist"))

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    icons_dir = os.path.join(frontend_dist, "icons")
    if os.path.exists(icons_dir):
        app.mount("/icons", StaticFiles(directory=icons_dir), name="icons")

    @app.get("/{rest_of_path:path}")
    async def serve_spa(rest_of_path: str):
        file_path = os.path.join(frontend_dist, rest_of_path)
        if rest_of_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
