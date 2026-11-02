"""
NetTracer - SQLite Persistent Storage Manager
Stores 1-minute aggregated app bandwidth statistics and manages history.
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger("nettracer.db")

DEFAULT_DB_DIR = "/var/lib/nettracer"
DEFAULT_DB_PATH = "/var/lib/nettracer/nettracer.db"
USER_FALLBACK_DB = os.path.expanduser("~/.local/share/nettracer/nettracer.db")


class DatabaseManager:
    """Manages SQLite database for historical network traffic and configuration."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = self._resolve_db_path(db_path)
        self._init_db()

    def _resolve_db_path(self, custom_path: Optional[str]) -> str:
        if custom_path:
            os.makedirs(os.path.dirname(custom_path), exist_ok=True)
            return custom_path

        # If running as root, use /var/lib/nettracer
        if os.geteuid() == 0:
            try:
                os.makedirs(DEFAULT_DB_DIR, mode=0o755, exist_ok=True)
                return DEFAULT_DB_PATH
            except OSError:
                pass

        # Otherwise fallback to user home directory or /tmp
        os.makedirs(os.path.dirname(USER_FALLBACK_DB), mode=0o755, exist_ok=True)
        return USER_FALLBACK_DB

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        logger.info(f"Initializing NetTracer database at: {self.db_path}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # History table for 1-minute aggregations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    pid INTEGER,
                    rx_bytes INTEGER NOT NULL,
                    tx_bytes INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_time ON app_usage_history(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_app ON app_usage_history(app_name);")

            # Key-Value settings store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

            # Seed initial sample history if empty for initial presentation
            cursor.execute("SELECT COUNT(*) FROM app_usage_history")
            if cursor.fetchone()[0] == 0:
                self._seed_sample_history(cursor)

            conn.commit()

    def _seed_sample_history(self, cursor: sqlite3.Cursor):
        """Initial sample history matching the prototype UI mockup."""
        now = datetime.now()
        samples = [
            ("Firefox", 450 * 1024 * 1024, 12 * 1024 * 1024, (now - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S")),
            ("Docker Daemon", 1200 * 1024 * 1024, 300 * 1024 * 1024, (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")),
            ("System Updates", 800 * 1024 * 1024, 2 * 1024 * 1024, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        ]
        for app, rx, tx, ts in samples:
            cursor.execute(
                "INSERT INTO app_usage_history (app_name, pid, rx_bytes, tx_bytes, timestamp) VALUES (?, ?, ?, ?, ?)",
                (app, 0, rx, tx, ts)
            )

    def save_minute_aggregates(self, aggregates: List[Dict[str, Any]]):
        """Saves a batch of 1-minute aggregated stats for apps."""
        if not aggregates:
            return
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for item in aggregates:
                rx = int(item.get("rx_bytes", 0))
                tx = int(item.get("tx_bytes", 0))
                if rx > 0 or tx > 0:
                    cursor.execute(
                        "INSERT INTO app_usage_history (app_name, pid, rx_bytes, tx_bytes, timestamp) VALUES (?, ?, ?, ?, ?)",
                        (item.get("app_name", "Unknown"), item.get("pid", 0), rx, tx, now_str)
                    )
            conn.commit()

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent app bandwidth history logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, app_name, pid, rx_bytes, tx_bytes, timestamp
                FROM app_usage_history
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def clear_history(self):
        """Clears all records from the usage history."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM app_usage_history")
            conn.commit()
            logger.info("Cleared usage history table.")

    def get_today_totals(self) -> Dict[str, int]:
        """Calculates total rx and tx bytes recorded since midnight."""
        today_start = datetime.now().strftime("%Y-%m-%d 00:00:00")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COALESCE(SUM(rx_bytes), 0) AS total_rx,
                       COALESCE(SUM(tx_bytes), 0) AS total_tx
                FROM app_usage_history
                WHERE timestamp >= ?
                """,
                (today_start,)
            )
            row = cursor.fetchone()
            return {
                "total_rx": int(row["total_rx"]),
                "total_tx": int(row["total_tx"]),
                "total": int(row["total_rx"]) + int(row["total_tx"])
            }

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def cleanup_retention(self, days: int):
        """Delete records older than specified days."""
        if days <= 0:
            return  # Forever
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute("DELETE FROM app_usage_history WHERE timestamp < ?", (cutoff,))
            conn.commit()
