"""
Entry point — initialises DB, starts scheduler, launches Flask+SocketIO.
"""
import logging
import sys
import os

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "app.log")),
    ],
)

import config
from database.models import init_db
from app import create_app
from scheduler.jobs import start_scheduler

logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("Options Paper Trader starting up")
    logger.info("Starting capital: $%.2f", config.STARTING_CAPITAL)
    logger.info("=" * 60)

    # 1. Initialise database
    init_db()
    logger.info("Database ready (Postgres)")

    # 2. Create Flask app + SocketIO
    app, socketio = create_app()

    # 3. Start background scheduler
    start_scheduler()
    logger.info("Scheduler running")

    # 4. Launch web server
    logger.info("Dashboard at http://127.0.0.1:%d", config.PORT)
    socketio.run(
        app,
        host="0.0.0.0",
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=False,   # avoid double-start with SocketIO
        log_output=False,
        allow_unsafe_werkzeug=True,   # dev server is fine for local paper trading
    )


if __name__ == "__main__":
    main()
