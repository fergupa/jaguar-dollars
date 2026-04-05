"""Database setup and connection helpers for Gator Dollars."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "gator_dollars.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS classrooms (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            teacher_id  INTEGER,
            pool_balance INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name  TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('teacher','student')),
            classroom_id  INTEGER REFERENCES classrooms(id),
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teacher_banks (
            teacher_id    INTEGER PRIMARY KEY REFERENCES users(id),
            balance       INTEGER NOT NULL DEFAULT 500,
            total_issued  INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS student_balances (
            student_id  INTEGER PRIMARY KEY REFERENCES users(id),
            balance     INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            type            TEXT NOT NULL CHECK(type IN (
                                'award','redemption','pool_contrib',
                                'pool_redemption','nomination_award'
                            )),
            from_user_id    INTEGER REFERENCES users(id),
            to_user_id      INTEGER REFERENCES users(id),
            amount          INTEGER NOT NULL,
            note            TEXT,
            classroom_id    INTEGER REFERENCES classrooms(id),
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS prizes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT,
            cost        INTEGER NOT NULL,
            prize_type  TEXT NOT NULL CHECK(prize_type IN ('individual','classroom')),
            quantity    INTEGER DEFAULT -1,
            emoji       TEXT DEFAULT '🎁',
            active      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS nominations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nominator_id    INTEGER NOT NULL REFERENCES users(id),
            nominee_id      INTEGER NOT NULL REFERENCES users(id),
            reason          TEXT NOT NULL,
            suggested_amount INTEGER DEFAULT 5,
            status          TEXT DEFAULT 'pending' CHECK(status IN ('pending','approved','denied')),
            reviewed_by     INTEGER REFERENCES users(id),
            review_note     TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at     TIMESTAMP
        );
    """)
    conn.close()


def is_db_empty() -> bool:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count == 0
