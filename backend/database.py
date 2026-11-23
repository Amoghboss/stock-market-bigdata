"""
SQLite helpers for the analytics dashboard.

Tables
------
processing_jobs  – log of every preprocessing / MapReduce run
analytics_cache  – JSON blob cache keyed by (cache_key)
system_logs      – general application-level log entries
"""
import sqlite3
import json
import os
from datetime import datetime
from backend.config import Config


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row-factory enabled."""
    Config.ensure_dirs()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ---------------------------------------------------------------------------
# Schema bootstrap
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS processing_jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type    TEXT    NOT NULL,          -- 'preprocess' | 'mapreduce'
    status      TEXT    NOT NULL DEFAULT 'pending',  -- pending | running | completed | failed
    started_at  TEXT,
    finished_at TEXT,
    details     TEXT,                      -- JSON blob with extra info
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analytics_cache (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key   TEXT    NOT NULL UNIQUE,
    cache_value TEXT    NOT NULL,          -- JSON
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at  TEXT                        -- optional TTL
);

CREATE TABLE IF NOT EXISTS system_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    level       TEXT    NOT NULL DEFAULT 'INFO',
    message     TEXT    NOT NULL,
    source      TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Processing jobs
# ---------------------------------------------------------------------------

def log_job(job_type: str, status: str = "pending", details: dict | None = None) -> int:
    """Insert a new processing job and return its id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO processing_jobs (job_type, status, started_at, details) VALUES (?, ?, ?, ?)",
            (job_type, status, datetime.utcnow().isoformat(), json.dumps(details or {})),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_job(job_id: int, status: str, details: dict | None = None):
    """Update the status (and optionally details) of a job."""
    conn = get_connection()
    try:
        finished = datetime.utcnow().isoformat() if status in ("completed", "failed") else None
        if details is not None:
            conn.execute(
                "UPDATE processing_jobs SET status=?, finished_at=?, details=? WHERE id=?",
                (status, finished, json.dumps(details), job_id),
            )
        else:
            conn.execute(
                "UPDATE processing_jobs SET status=?, finished_at=? WHERE id=?",
                (status, finished, job_id),
            )
        conn.commit()
    finally:
        conn.close()


def get_jobs(job_type: str | None = None, limit: int = 50) -> list[dict]:
    """Return recent jobs, optionally filtered by type."""
    conn = get_connection()
    try:
        if job_type:
            rows = conn.execute(
                "SELECT * FROM processing_jobs WHERE job_type=? ORDER BY id DESC LIMIT ?",
                (job_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM processing_jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_latest_job(job_type: str) -> dict | None:
    """Return the most recent job of the given type, or None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM processing_jobs WHERE job_type=? ORDER BY id DESC LIMIT 1",
            (job_type,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Analytics cache
# ---------------------------------------------------------------------------

def cache_get(key: str) -> dict | list | None:
    """Return cached JSON value or None if missing / expired."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT cache_value, expires_at FROM analytics_cache WHERE cache_key=?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        if row["expires_at"] and row["expires_at"] < datetime.utcnow().isoformat():
            conn.execute("DELETE FROM analytics_cache WHERE cache_key=?", (key,))
            conn.commit()
            return None
        return json.loads(row["cache_value"])
    finally:
        conn.close()


def cache_set(key: str, value, expires_at: str | None = None):
    """Upsert a cache entry."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO analytics_cache (cache_key, cache_value, expires_at)
               VALUES (?, ?, ?)
               ON CONFLICT(cache_key) DO UPDATE SET cache_value=excluded.cache_value,
                                                     expires_at=excluded.expires_at,
                                                     created_at=datetime('now')""",
            (key, json.dumps(value), expires_at),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# System logs
# ---------------------------------------------------------------------------

def add_log(message: str, level: str = "INFO", source: str | None = None):
    """Write a log entry to the database."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO system_logs (level, message, source) VALUES (?, ?, ?)",
            (level, message, source),
        )
        conn.commit()
    finally:
        conn.close()


def get_logs(level: str | None = None, limit: int = 100) -> list[dict]:
    """Return recent log entries."""
    conn = get_connection()
    try:
        if level:
            rows = conn.execute(
                "SELECT * FROM system_logs WHERE level=? ORDER BY id DESC LIMIT ?",
                (level, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM system_logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
