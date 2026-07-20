"""
Flask web application — dashboard API + SocketIO for real-time updates.
"""
import json
import logging
from datetime import datetime

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO

import config
from database.models import (
    get_portfolio, get_open_positions, get_recent_signals,
    get_recent_trades, get_portfolio_history, get_recent_logs,
    get_algo_params, update_algo_param, log_event
)
from scheduler.jobs import (
    start_scheduler, set_socketio,
    run_scan_now, run_position_check_now, run_tune_now
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sw.js")
def service_worker():
    # Served from root (not /static/) so its default scope covers the whole app.
    response = send_from_directory(app.static_folder, "sw.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


# ── REST API ───────────────────────────────────────────────────────────────────

@app.route("/api/portfolio")
def api_portfolio():
    pf       = get_portfolio()
    open_pos = get_open_positions()
    history  = get_portfolio_history(limit=90)

    invested = sum(
        p["premium_collected"] for p in open_pos
        if p["position_type"] in ("SELL_PUT", "SELL_CALL")
    )
    stock_value = sum(
        (p.get("current_premium") or 0) for p in open_pos
        if p["position_type"] == "LONG_STOCK"
    )

    return jsonify({
        "cash":           round(pf["cash"], 2),
        "total_value":    round(pf["total_value"], 2),
        "starting_value": config.STARTING_CAPITAL,
        "total_pnl":      round(pf["total_value"] - config.STARTING_CAPITAL, 2),
        "total_pnl_pct":  round((pf["total_value"] - config.STARTING_CAPITAL)
                                 / config.STARTING_CAPITAL * 100, 2),
        "open_positions": len(open_pos),
        "history":        history,
    })


@app.route("/api/positions")
def api_positions():
    pos = get_open_positions()
    # Enrich with unrealised P&L display
    for p in pos:
        orig = p.get("premium_collected", 0) or 0
        curr = p.get("current_premium",   0) or 0
        p["unrealised_pnl"]     = round(orig - curr, 2)
        p["unrealised_pnl_pct"] = round((orig - curr) / orig * 100, 2) if orig else 0
    return jsonify(pos)


@app.route("/api/signals")
def api_signals():
    return jsonify(get_recent_signals(limit=30))


@app.route("/api/trades")
def api_trades():
    return jsonify(get_recent_trades(limit=50))


@app.route("/api/logs")
def api_logs():
    return jsonify(get_recent_logs(limit=100))


@app.route("/api/params")
def api_params():
    return jsonify(get_algo_params())


@app.route("/api/params", methods=["POST"])
def api_update_param():
    data = request.json or {}
    name  = data.get("name")
    value = data.get("value")
    if not name or value is None:
        return jsonify({"error": "name and value required"}), 400
    try:
        update_algo_param(name, float(value))
        log_event("app", f"Param updated: {name}={value}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Manual trigger endpoints ───────────────────────────────────────────────────

@app.route("/api/trigger/scan", methods=["POST"])
def trigger_scan():
    result = run_scan_now()
    log_event("app", "Manual scan triggered via UI")
    return jsonify(result)


@app.route("/api/trigger/check", methods=["POST"])
def trigger_check():
    result = run_position_check_now()
    log_event("app", "Manual position check triggered via UI")
    return jsonify(result)


@app.route("/api/trigger/tune", methods=["POST"])
def trigger_tune():
    result = run_tune_now()
    log_event("app", "Manual self-tune triggered via UI")
    return jsonify(result)


# ── SocketIO events ────────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    logger.info("Client connected")


@socketio.on("disconnect")
def on_disconnect():
    logger.info("Client disconnected")


# ── App factory ────────────────────────────────────────────────────────────────

def create_app():
    set_socketio(socketio)
    return app, socketio
