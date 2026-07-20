"""
APScheduler background jobs.

Jobs:
  daily_scan         — 10:00 AM ET weekdays: scan universe, open new positions
  position_check     — every 30 min, weekday market hours: manage open positions
  end_of_day_update  — 4:15 PM ET weekdays: snapshot portfolio value
  monthly_tune       — every 30 days: self-tune algorithm parameters
"""
import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron         import CronTrigger
from apscheduler.triggers.interval     import IntervalTrigger

import config
from database.models import log_event, update_portfolio, get_portfolio
from trading.scanner          import scan_universe
from trading.strategy         import select_put_to_sell
from trading.position_manager import check_and_manage_positions
from scheduler.self_tuner     import run_self_tune

logger = logging.getLogger(__name__)
ET = pytz.timezone("US/Eastern")

_scheduler: BackgroundScheduler = None


# ── Job functions ──────────────────────────────────────────────────────────────

def job_daily_scan():
    """Morning scan: find candidates and open positions."""
    try:
        log_event("scheduler", "=== Daily scan starting ===")
        signals  = scan_universe()
        executed = select_put_to_sell(signals)
        log_event("scheduler",
                  f"Daily scan done — {len(signals)} signals, {len(executed)} trades opened")
        _emit_update("scan_complete", {"signals": len(signals), "trades": len(executed)})
    except Exception as e:
        logger.error("daily_scan error: %s", e)
        log_event("scheduler", f"Daily scan error: {e}", "ERROR")


def job_position_check():
    """Periodic position check during market hours."""
    now_et = datetime.now(ET)
    # Only run during market hours Mon-Fri 9:30-16:00 ET
    if now_et.weekday() >= 5:
        return
    hour, minute = now_et.hour, now_et.minute
    if not ((9 < hour < 16) or (hour == 9 and minute >= 30)):
        return
    try:
        result = check_and_manage_positions()
        if result["actions"]:
            _emit_update("positions_updated", result)
    except Exception as e:
        logger.error("position_check error: %s", e)
        log_event("scheduler", f"Position check error: {e}", "ERROR")


def job_end_of_day():
    """End-of-day portfolio snapshot."""
    try:
        from trading.position_manager import _update_portfolio_value
        _update_portfolio_value()
        pf = get_portfolio()
        log_event("scheduler",
                  f"EOD snapshot: total=${pf['total_value']:.2f} cash=${pf['cash']:.2f}")
        _emit_update("eod_update", {"total_value": pf["total_value"], "cash": pf["cash"]})
    except Exception as e:
        logger.error("end_of_day error: %s", e)
        log_event("scheduler", f"EOD error: {e}", "ERROR")


def job_monthly_tune():
    """Monthly self-tuning job."""
    try:
        run_self_tune()
        _emit_update("algo_tuned", {})
    except Exception as e:
        logger.error("monthly_tune error: %s", e)
        log_event("scheduler", f"Monthly tune error: {e}", "ERROR")


# ── Real-time push helper ──────────────────────────────────────────────────────

_socketio = None

def set_socketio(sio):
    global _socketio
    _socketio = sio


def _emit_update(event: str, data: dict):
    if _socketio:
        try:
            _socketio.emit(event, data, namespace="/")
        except Exception:
            pass


# ── Scheduler lifecycle ───────────────────────────────────────────────────────

def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone=ET)

    # Daily scan — 10:00 AM ET, Mon–Fri
    _scheduler.add_job(
        job_daily_scan,
        CronTrigger(hour=config.SCAN_HOUR, minute=config.SCAN_MINUTE,
                    day_of_week="mon-fri", timezone=ET),
        id="daily_scan",
        replace_existing=True,
    )

    # Position check — every 30 min
    _scheduler.add_job(
        job_position_check,
        IntervalTrigger(minutes=config.CHECK_INTERVAL_MINUTES),
        id="position_check",
        replace_existing=True,
    )

    # EOD update — 4:15 PM ET, Mon–Fri
    _scheduler.add_job(
        job_end_of_day,
        CronTrigger(hour=config.EOD_HOUR, minute=config.EOD_MINUTE,
                    day_of_week="mon-fri", timezone=ET),
        id="end_of_day",
        replace_existing=True,
    )

    # Monthly self-tune
    _scheduler.add_job(
        job_monthly_tune,
        CronTrigger(day=1, hour=8, minute=0, timezone=ET),
        id="monthly_tune",
        replace_existing=True,
    )

    _scheduler.start()
    log_event("scheduler", "Scheduler started")
    logger.info("APScheduler started with %d jobs", len(_scheduler.get_jobs()))


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log_event("scheduler", "Scheduler stopped")


# ── Manual triggers (for UI buttons) ─────────────────────────────────────────

def run_scan_now():
    """Trigger a manual scan immediately."""
    import threading
    t = threading.Thread(target=job_daily_scan, daemon=True)
    t.start()
    return {"status": "scan started"}


def run_position_check_now():
    """Trigger a manual position check immediately."""
    import threading
    t = threading.Thread(target=job_position_check, daemon=True)
    t.start()
    return {"status": "position check started"}


def run_tune_now():
    """Trigger self-tuning immediately."""
    import threading
    t = threading.Thread(target=job_monthly_tune, daemon=True)
    t.start()
    return {"status": "tuning started"}
