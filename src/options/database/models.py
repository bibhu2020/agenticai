"""
PostgreSQL (Neon) database models and helpers.
"""
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

import config

# ── Connection helper ─────────────────────────────────────────────────────────

# Matches sqlite's old `datetime('now')` output: 'YYYY-MM-DD HH:MM:SS', UTC.
_NOW_EXPR = "to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')"


@contextmanager
def get_db():
    conn = psycopg.connect(config.DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema ────────────────────────────────────────────────────────────────────
# Statements are ordered so REFERENCES targets already exist (Postgres, unlike
# sqlite, enforces this at CREATE TABLE time).

SCHEMA_STATEMENTS = [
    f"""
    CREATE TABLE IF NOT EXISTS portfolio (
        id            SERIAL  PRIMARY KEY,
        cash          DOUBLE PRECISION NOT NULL DEFAULT 5000.0,
        total_value   DOUBLE PRECISION NOT NULL DEFAULT 5000.0,
        created_at    TEXT    NOT NULL DEFAULT ({_NOW_EXPR}),
        updated_at    TEXT    NOT NULL DEFAULT ({_NOW_EXPR})
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS signals (
        id                   SERIAL  PRIMARY KEY,
        ticker               TEXT    NOT NULL,
        composite_score      DOUBLE PRECISION NOT NULL DEFAULT 0,
        technical_score      DOUBLE PRECISION NOT NULL DEFAULT 0,
        fundamental_score    DOUBLE PRECISION NOT NULL DEFAULT 0,
        sentiment_score      DOUBLE PRECISION NOT NULL DEFAULT 0,
        current_price        DOUBLE PRECISION,
        recommended_strike   DOUBLE PRECISION,
        recommended_expiry   TEXT,
        estimated_premium    DOUBLE PRECISION,
        implied_volatility   DOUBLE PRECISION,
        status               TEXT    NOT NULL DEFAULT 'PENDING',
        skip_reason          TEXT,
        created_at           TEXT    NOT NULL DEFAULT ({_NOW_EXPR})
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS positions (
        id                SERIAL  PRIMARY KEY,
        ticker            TEXT    NOT NULL,
        position_type     TEXT    NOT NULL,
        strike            DOUBLE PRECISION,
        expiry            TEXT,
        contracts         INTEGER NOT NULL DEFAULT 1,
        underlying_price  DOUBLE PRECISION,
        premium_collected DOUBLE PRECISION NOT NULL DEFAULT 0,
        current_premium   DOUBLE PRECISION NOT NULL DEFAULT 0,
        entry_date        TEXT    NOT NULL DEFAULT ({_NOW_EXPR}),
        exit_date         TEXT,
        status            TEXT    NOT NULL DEFAULT 'OPEN',
        pnl               DOUBLE PRECISION NOT NULL DEFAULT 0,
        pnl_pct           DOUBLE PRECISION NOT NULL DEFAULT 0,
        close_reason      TEXT,
        signal_id         INTEGER REFERENCES signals(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trades (
        id           SERIAL  PRIMARY KEY,
        position_id  INTEGER REFERENCES positions(id),
        ticker       TEXT    NOT NULL,
        action       TEXT    NOT NULL,
        strike       DOUBLE PRECISION,
        expiry       TEXT,
        contracts    INTEGER NOT NULL DEFAULT 1,
        price        DOUBLE PRECISION NOT NULL,
        total_value  DOUBLE PRECISION NOT NULL,
        timestamp    TEXT    NOT NULL DEFAULT (%s),
        notes        TEXT
    )
    """ % _NOW_EXPR,
    """
    CREATE TABLE IF NOT EXISTS algo_params (
        id           SERIAL  PRIMARY KEY,
        param_name   TEXT    NOT NULL UNIQUE,
        param_value  DOUBLE PRECISION NOT NULL,
        updated_at   TEXT    NOT NULL DEFAULT (%s)
    )
    """ % _NOW_EXPR,
    """
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id                  SERIAL  PRIMARY KEY,
        period_start        TEXT    NOT NULL,
        period_end          TEXT    NOT NULL,
        total_trades        INTEGER NOT NULL DEFAULT 0,
        winning_trades      INTEGER NOT NULL DEFAULT 0,
        win_rate            DOUBLE PRECISION NOT NULL DEFAULT 0,
        total_pnl           DOUBLE PRECISION NOT NULL DEFAULT 0,
        avg_pnl_per_trade   DOUBLE PRECISION NOT NULL DEFAULT 0,
        portfolio_value     DOUBLE PRECISION NOT NULL DEFAULT 0,
        recorded_at         TEXT    NOT NULL DEFAULT (%s)
    )
    """ % _NOW_EXPR,
    """
    CREATE TABLE IF NOT EXISTS portfolio_history (
        id            SERIAL  PRIMARY KEY,
        total_value   DOUBLE PRECISION NOT NULL,
        cash          DOUBLE PRECISION NOT NULL,
        timestamp     TEXT    NOT NULL DEFAULT (%s)
    )
    """ % _NOW_EXPR,
    """
    CREATE TABLE IF NOT EXISTS logs (
        id         SERIAL  PRIMARY KEY,
        level      TEXT NOT NULL DEFAULT 'INFO',
        module     TEXT NOT NULL DEFAULT 'system',
        message    TEXT NOT NULL,
        timestamp  TEXT NOT NULL DEFAULT (%s)
    )
    """ % _NOW_EXPR,
]


def init_db():
    """Create tables and seed default data if needed."""
    with get_db() as conn:
        for stmt in SCHEMA_STATEMENTS:
            conn.execute(stmt)

        # Migrate: add signal_id to positions if upgrading from an older DB
        cols = [
            r["column_name"] for r in conn.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'positions'"
            ).fetchall()
        ]
        if "signal_id" not in cols:
            conn.execute("ALTER TABLE positions ADD COLUMN signal_id INTEGER REFERENCES signals(id)")

        # Seed portfolio row if empty
        row = conn.execute("SELECT COUNT(*) AS n FROM portfolio").fetchone()["n"]
        if row == 0:
            conn.execute(
                "INSERT INTO portfolio (cash, total_value) VALUES (%s, %s)",
                (config.STARTING_CAPITAL, config.STARTING_CAPITAL),
            )

        # Seed default algo params
        defaults = {
            "weight_technical":    config.WEIGHT_TECHNICAL,
            "weight_fundamental":  config.WEIGHT_FUNDAMENTAL,
            "weight_sentiment":    config.WEIGHT_SENTIMENT,
            "min_score_to_trade":  config.MIN_SCORE_TO_TRADE,
            "target_delta":        config.TARGET_DELTA,
            "min_dte":             config.MIN_DTE,
            "max_dte":             config.MAX_DTE,
            "profit_target_pct":   config.PROFIT_TARGET_PCT,
            "stop_loss_pct":       config.STOP_LOSS_PCT,
            "max_position_size_pct": config.MAX_POSITION_SIZE_PCT,
        }
        for name, value in defaults.items():
            conn.execute(
                """INSERT INTO algo_params (param_name, param_value)
                   VALUES (%s, %s) ON CONFLICT (param_name) DO NOTHING""",
                (name, value),
            )

        # Seed initial portfolio snapshot
        conn.execute(
            "INSERT INTO portfolio_history (total_value, cash) VALUES (%s, %s)",
            (config.STARTING_CAPITAL, config.STARTING_CAPITAL),
        )

    log_event("system", "Database initialised", "INFO")


# ── CRUD helpers ──────────────────────────────────────────────────────────────

def get_portfolio():
    with get_db() as conn:
        row = conn.execute("SELECT * FROM portfolio WHERE id = 1").fetchone()
        return dict(row) if row else None


def update_portfolio(cash=None, total_value=None):
    updates, vals = [], []
    if cash is not None:
        updates.append("cash = %s"); vals.append(cash)
    if total_value is not None:
        updates.append("total_value = %s"); vals.append(total_value)
    if not updates:
        return
    updates.append(f"updated_at = {_NOW_EXPR}")
    with get_db() as conn:
        conn.execute(f"UPDATE portfolio SET {', '.join(updates)} WHERE id = 1", vals)
        conn.execute(
            "INSERT INTO portfolio_history (total_value, cash) VALUES (%s, %s)",
            (total_value or get_portfolio()["total_value"],
             cash or get_portfolio()["cash"]),
        )


def get_open_positions():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM positions WHERE status = 'OPEN' ORDER BY entry_date DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_position(position_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM positions WHERE id = %s", (position_id,)).fetchone()
        return dict(row) if row else None


def create_position(ticker, position_type, strike, expiry, contracts,
                    underlying_price, premium_collected, signal_id=None):
    with get_db() as conn:
        row = conn.execute(
            """INSERT INTO positions
               (ticker, position_type, strike, expiry, contracts,
                underlying_price, premium_collected, current_premium, signal_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (ticker, position_type, strike, expiry, contracts,
             underlying_price, premium_collected, premium_collected, signal_id),
        ).fetchone()
        return row["id"]


def update_position(position_id, **kwargs):
    sets, vals = [], []
    for k, v in kwargs.items():
        sets.append(f"{k} = %s"); vals.append(v)
    if not sets:
        return
    vals.append(position_id)
    with get_db() as conn:
        conn.execute(
            f"UPDATE positions SET {', '.join(sets)} WHERE id = %s", vals
        )


def close_position(position_id, pnl, pnl_pct, close_reason, current_premium):
    with get_db() as conn:
        conn.execute(
            f"""UPDATE positions
               SET status='CLOSED', exit_date={_NOW_EXPR},
                   pnl=%s, pnl_pct=%s, close_reason=%s, current_premium=%s
               WHERE id=%s""",
            (pnl, pnl_pct, close_reason, current_premium, position_id),
        )


def record_trade(position_id, ticker, action, strike, expiry,
                 contracts, price, total_value, notes=""):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO trades
               (position_id, ticker, action, strike, expiry,
                contracts, price, total_value, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (position_id, ticker, action, strike, expiry,
             contracts, price, total_value, notes),
        )


def create_signal(ticker, scores: dict, price, strike, expiry, premium, iv):
    with get_db() as conn:
        row = conn.execute(
            """INSERT INTO signals
               (ticker, composite_score, technical_score, fundamental_score,
                sentiment_score, current_price, recommended_strike,
                recommended_expiry, estimated_premium, implied_volatility)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (ticker,
             scores.get("composite", 0),
             scores.get("technical", 0),
             scores.get("fundamental", 0),
             scores.get("sentiment", 0),
             price, strike, expiry, premium, iv),
        ).fetchone()
        return row["id"]


def update_signal(signal_id, status, skip_reason=None):
    with get_db() as conn:
        conn.execute(
            "UPDATE signals SET status=%s, skip_reason=%s WHERE id=%s",
            (status, skip_reason, signal_id),
        )


def get_algo_params():
    with get_db() as conn:
        rows = conn.execute("SELECT param_name, param_value FROM algo_params").fetchall()
        return {r["param_name"]: r["param_value"] for r in rows}


def update_algo_param(name, value):
    with get_db() as conn:
        conn.execute(
            f"""INSERT INTO algo_params (param_name, param_value, updated_at)
               VALUES (%s, %s, {_NOW_EXPR})
               ON CONFLICT (param_name) DO UPDATE
               SET param_value = EXCLUDED.param_value, updated_at = EXCLUDED.updated_at""",
            (name, value),
        )


def record_performance(period_start, period_end, total_trades, winning_trades,
                       win_rate, total_pnl, avg_pnl, portfolio_value):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO performance_metrics
               (period_start, period_end, total_trades, winning_trades,
                win_rate, total_pnl, avg_pnl_per_trade, portfolio_value)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (period_start, period_end, total_trades, winning_trades,
             win_rate, total_pnl, avg_pnl, portfolio_value),
        )


def get_closed_trades_since(since_date: str):
    """
    Closed positions since `since_date`, left-joined with the signal that
    opened them so callers can see the technical/fundamental/sentiment
    sub-scores behind each trade (NULL when no signal was linked).
    """
    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.*,
                      s.technical_score   AS signal_technical_score,
                      s.fundamental_score AS signal_fundamental_score,
                      s.sentiment_score   AS signal_sentiment_score
               FROM positions p
               LEFT JOIN signals s ON s.id = p.signal_id
               WHERE p.status='CLOSED' AND p.exit_date >= %s
               ORDER BY p.exit_date DESC""",
            (since_date,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_portfolio_history(limit=90):
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM portfolio_history
               ORDER BY timestamp DESC LIMIT %s""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in reversed(rows)]


def get_recent_signals(limit=20):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM signals ORDER BY created_at DESC LIMIT %s",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_trades(limit=50):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM trades ORDER BY timestamp DESC LIMIT %s",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def log_event(module: str, message: str, level: str = "INFO"):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO logs (level, module, message) VALUES (%s, %s, %s)",
                (level, module, message),
            )
    except Exception:
        pass  # Never crash because of logging


def get_recent_logs(limit=100):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY timestamp DESC LIMIT %s",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
