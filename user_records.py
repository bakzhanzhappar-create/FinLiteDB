# -*- coding: utf-8 -*-
"""
Отдельная SQLite-база на пользователя: {username}_records.db
Таблица History — факты использования шаблона и введённая сумма.
"""
import json
import re
import sqlite3
from pathlib import Path
from typing import List, Optional

RECORDS_DIR = Path(__file__).resolve().parent / "records"

CREATE_HISTORY_SQL = """
CREATE TABLE IF NOT EXISTS History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    template_name TEXT NOT NULL,
    input_amount REAL NOT NULL,
    remainder REAL NOT NULL,
    fail_rule_index INTEGER,
    history_json TEXT
);
"""


def _safe_username(username: str) -> str:
    u = (username or "guest").strip().lower()
    u = re.sub(r"[^a-z0-9_-]", "_", u)
    return u or "guest"


def db_path(username: str) -> Path:
    """Путь к файлу БД, например records/baga_records.db для пользователя baga."""
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    return RECORDS_DIR / f"{_safe_username(username)}_records.db"


def ensure_connection(username: str) -> sqlite3.Connection:
    path = db_path(username)
    conn = sqlite3.connect(str(path))
    conn.execute(CREATE_HISTORY_SQL)
    conn.commit()
    return conn


def log_fifo_use(
    username: str,
    template_name: str,
    input_amount: float,
    remainder: float,
    fail_rule_index: Optional[int],
    history_lines: List[str],
) -> None:
    """Запись в History после успешного расчёта FIFO по выбранному шаблону."""
    try:
        conn = ensure_connection(username)
        conn.execute(
            """
            INSERT INTO History (template_name, input_amount, remainder, fail_rule_index, history_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                template_name,
                float(input_amount),
                float(remainder),
                fail_rule_index,
                json.dumps(history_lines, ensure_ascii=False),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def fetch_recent(username: str, limit: int = 50) -> List[dict]:
    """Последние записи History (для отладки или UI)."""
    try:
        conn = ensure_connection(username)
        cur = conn.execute(
            """
            SELECT id, created_at, template_name, input_amount, remainder, fail_rule_index, history_json
            FROM History
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r[0],
                    "created_at": r[1],
                    "template_name": r[2],
                    "input_amount": r[3],
                    "remainder": r[4],
                    "fail_rule_index": r[5],
                    "history_json": r[6],
                }
            )
        return out
    except Exception:
        return []


def prefs_path(username: str) -> Path:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    return RECORDS_DIR / f"{_safe_username(username)}_prefs.json"


def load_ui_prefs(username: str) -> dict:
    try:
        with open(prefs_path(username), encoding="utf-8") as f:
            d = json.load(f)
            if not isinstance(d, dict):
                return {"theme": "light"}
            return d
    except Exception:
        return {"theme": "light"}


def save_ui_theme(username: str, theme: str) -> None:
    theme = "dark" if theme == "dark" else "light"
    data = load_ui_prefs(username)
    data["theme"] = theme
    with open(prefs_path(username), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
