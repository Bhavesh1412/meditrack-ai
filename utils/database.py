"""
database.py - Database initialization and connection utilities
Handles SQLite database setup for Nabz AI
"""

import sqlite3
import os

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')


def get_db_connection():
    """
    Create and return a database connection.
    Uses row_factory so results behave like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name: row['column_name']
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
    return conn


def init_db():
    """
    Initialize all database tables.
    Called once when the app starts — safe to call multiple times (IF NOT EXISTS).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ─── USERS TABLE ────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,          -- bcrypt hashed
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ─── MEDICINES TABLE ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT    NOT NULL,
            dosage      TEXT    NOT NULL,           -- e.g., "500mg"
            frequency   TEXT    NOT NULL,           -- e.g., "Twice daily"
            time        TEXT    NOT NULL,           -- e.g., "08:00,20:00"
            start_date  TEXT    NOT NULL,
            end_date    TEXT,
            notes       TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ─── REMINDERS TABLE ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            medicine_id  INTEGER NOT NULL,
            reminder_time TEXT   NOT NULL,          -- "HH:MM"
            is_active    INTEGER DEFAULT 1,
            created_at   TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        )
    """)

    # ─── MEDICATION HISTORY TABLE ────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medication_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            medicine_id  INTEGER NOT NULL,
            status       TEXT    NOT NULL CHECK(status IN ('taken', 'missed', 'skipped')),
            taken_at     TEXT    DEFAULT (datetime('now')),
            scheduled_time TEXT,
            notes        TEXT,
            FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        )
    """)

    # ─── SIDE EFFECTS TABLE ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS side_effects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            medicine_id INTEGER,                    -- optional: link to a specific medicine
            symptom     TEXT    NOT NULL,
            severity    TEXT    NOT NULL CHECK(severity IN ('mild', 'moderate', 'severe')),
            description TEXT,
            reported_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)     REFERENCES users(id)     ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE SET NULL
        )
    """)

    # ─── CHAT HISTORY TABLE ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            role        TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
            message     TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ─── HEALTH VAULT TABLE ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_vault (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            file_name      TEXT    NOT NULL,
            original_name  TEXT    NOT NULL,
            file_type      TEXT    NOT NULL,
            file_path      TEXT    NOT NULL,
            file_size      INTEGER,
            ai_summary     TEXT,
            ai_conflicts   TEXT,
            ai_suggestions TEXT,
            ai_analysed_at TEXT,
            uploaded_at    TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ─── VAULT CHAT TABLE ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_chat (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            vault_id   INTEGER,
            role       TEXT    NOT NULL CHECK(role IN ('user', 'assistant')),
            message    TEXT    NOT NULL,
            created_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id)  REFERENCES users(id)            ON DELETE CASCADE,
            FOREIGN KEY (vault_id) REFERENCES health_vault(id)     ON DELETE SET NULL
        )
    """)

    conn.commit()

    # ─── MIGRATIONS ───────────────────────────────────────────────────────────
    # Backfill columns that may be missing from databases created by an older
    # schema (CREATE TABLE IF NOT EXISTS won't add columns to existing tables).
    # SQLite only allows constant defaults when adding a column, so datetime
    # columns are added without a default and backfilled via UPDATE.
    _add_column_if_missing(conn, 'medicines', 'is_active', 'INTEGER DEFAULT 1')
    _add_column_if_missing(conn, 'medicines', 'created_at', 'TEXT')
    _add_column_if_missing(conn, 'reminders', 'is_active', 'INTEGER DEFAULT 1')
    _add_column_if_missing(conn, 'reminders', 'created_at', 'TEXT')
    _add_column_if_missing(conn, 'medication_history', 'created_at', 'TEXT')
    _add_column_if_missing(conn, 'side_effects', 'created_at', 'TEXT')
    _add_column_if_missing(conn, 'chat_history', 'created_at', 'TEXT')
    _add_column_if_missing(conn, 'health_vault', 'uploaded_at', 'TEXT')
    _add_column_if_missing(conn, 'vault_chat', 'created_at', 'TEXT')

    # Backfill any NULL timestamps created by the migration above.
    for table, col in [
        ('medicines', 'created_at'), ('reminders', 'created_at'),
        ('medication_history', 'created_at'), ('side_effects', 'created_at'),
        ('chat_history', 'created_at'), ('health_vault', 'uploaded_at'),
        ('vault_chat', 'created_at'),
    ]:
        conn.execute(f"UPDATE {table} SET {col} = datetime('now') WHERE {col} IS NULL")
    conn.execute("UPDATE medicines SET is_active = 1 WHERE is_active IS NULL")

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def _add_column_if_missing(conn, table, column, definition):
    """Add `column` to `table` only if it does not already exist."""
    exists = conn.execute(f"PRAGMA table_info({table})").fetchall()
    if column not in [row[1] for row in exists]:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
