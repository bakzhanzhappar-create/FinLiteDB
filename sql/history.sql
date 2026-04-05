-- Файл БД на пользователя: records/{username}_records.db (например baga -> records/baga_records.db)
-- Таблица создаётся при первом обращении (CREATE TABLE IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    template_name TEXT NOT NULL,
    input_amount REAL NOT NULL,
    remainder REAL NOT NULL,
    fail_rule_index INTEGER,
    history_json TEXT
);
