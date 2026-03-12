"""Database and statistics logic for TypeSlate Terminal.

Shares the same SQLite database as the desktop TypeSlate app so stats
are unified across both versions.
"""

import os
import re
import sqlite3
from datetime import datetime, timedelta


def get_data_directory() -> str:
    import sys
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        # Linux/BSD — follow XDG
        base = os.getenv("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
    base_dir = os.path.join(base, "TypeSlate")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def get_db_path() -> str:
    return os.path.join(get_data_directory(), "stats.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    return conn


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_count INTEGER,
        duration REAL,
        timestamp TEXT,
        misspelled_words INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS total_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total_word_count INTEGER,
        largest_word_count INTEGER
    )""")
    conn.commit()
    conn.close()


def load_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT total_word_count, largest_word_count FROM total_stats WHERE id = 1")
    row = cursor.fetchone()
    total_word_count = row[0] if row else 0
    largest_word_count = row[1] if row else 0

    cursor.execute("SELECT word_count, duration, timestamp, misspelled_words FROM sessions ORDER BY timestamp DESC")
    sessions = [
        {"word_count": r[0], "duration": r[1], "timestamp": r[2], "misspelled_words": r[3]}
        for r in cursor.fetchall()
    ]
    conn.close()

    return {
        "total_word_count": total_word_count,
        "largest_word_count": largest_word_count,
        "sessions": sessions,
    }


def save_session(word_count: int, duration: float, misspelled_words: int):
    """Save a completed writing session to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        "INSERT INTO sessions (word_count, duration, timestamp, misspelled_words) VALUES (?, ?, ?, ?)",
        (word_count, duration, timestamp, misspelled_words),
    )

    # Update totals
    cursor.execute("SELECT total_word_count, largest_word_count FROM total_stats WHERE id = 1")
    row = cursor.fetchone()
    if row:
        new_total = row[0] + word_count
        new_largest = max(row[1], word_count)
        cursor.execute(
            "UPDATE total_stats SET total_word_count = ?, largest_word_count = ? WHERE id = 1",
            (new_total, new_largest),
        )
    else:
        cursor.execute(
            "INSERT INTO total_stats (id, total_word_count, largest_word_count) VALUES (1, ?, ?)",
            (word_count, word_count),
        )

    conn.commit()
    conn.close()


def get_period_stats() -> dict:
    """Get word counts for today, yesterday, 7-day, 30-day, and lifetime."""
    conn = get_connection()
    cursor = conn.cursor()

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    cursor.execute("SELECT word_count, timestamp FROM sessions")
    rows = cursor.fetchall()

    today_wc = 0
    yesterday_wc = 0
    week_wc = 0
    month_wc = 0
    total_wc = 0
    session_count = len(rows)

    for wc, ts in rows:
        total_wc += wc
        try:
            session_date = datetime.fromisoformat(ts).date()
        except (ValueError, TypeError):
            continue
        if session_date == today:
            today_wc += wc
        if session_date == yesterday:
            yesterday_wc += wc
        if session_date >= week_ago:
            week_wc += wc
        if session_date >= month_ago:
            month_wc += wc

    cursor.execute("SELECT largest_word_count FROM total_stats WHERE id = 1")
    row = cursor.fetchone()
    largest = row[0] if row else 0

    conn.close()

    return {
        "today": today_wc,
        "yesterday": yesterday_wc,
        "week": week_wc,
        "month": month_wc,
        "total": total_wc,
        "largest_session": largest,
        "session_count": session_count,
    }


def analyze_text(text: str) -> int:
    """Return the number of misspelled words in the text."""
    try:
        from spellchecker import SpellChecker

        spell = SpellChecker()
        words = re.findall(r"\b\w+\b", text)
        unknown = spell.unknown(words)

        filtered = set()
        for word in unknown:
            if word.isupper():
                continue
            if word[0].isupper() and word.lower() not in spell:
                continue
            if len(word) < 3:
                continue
            filtered.add(word)

        return len(filtered)
    except Exception:
        return 0


def get_save_folder() -> str:
    """Get the last-used save folder, or create a default one."""
    last_folder_file = os.path.join(get_data_directory(), "last_folder.txt")
    try:
        with open(last_folder_file, "r") as f:
            folder = f.read().strip()
            if os.path.isdir(folder):
                return folder
    except FileNotFoundError:
        pass

    # Default save folder
    default = os.path.join(get_data_directory(), "sessions")
    os.makedirs(default, exist_ok=True)
    return default


def set_save_folder(folder: str):
    last_folder_file = os.path.join(get_data_directory(), "last_folder.txt")
    with open(last_folder_file, "w") as f:
        f.write(folder)


def get_templates_folder() -> str:
    """Get the templates folder, or create a default one."""
    templates_file = os.path.join(get_data_directory(), "templates_folder.txt")
    try:
        with open(templates_file, "r") as f:
            folder = f.read().strip()
            if os.path.isdir(folder):
                return folder
    except FileNotFoundError:
        pass

    default = os.path.join(get_data_directory(), "templates")
    os.makedirs(default, exist_ok=True)
    return default


def set_templates_folder(folder: str):
    templates_file = os.path.join(get_data_directory(), "templates_folder.txt")
    with open(templates_file, "w") as f:
        f.write(folder)


def get_last_theme() -> str:
    theme_file = os.path.join(get_data_directory(), "last_theme.txt")
    try:
        with open(theme_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Warm Dark"


def save_theme(theme: str):
    theme_file = os.path.join(get_data_directory(), "last_theme.txt")
    with open(theme_file, "w") as f:
        f.write(theme)


def save_last_session_path(filepath: str):
    p = os.path.join(get_data_directory(), "last_session.txt")
    with open(p, "w") as f:
        f.write(filepath)


def get_last_session_path() -> str | None:
    p = os.path.join(get_data_directory(), "last_session.txt")
    try:
        with open(p, "r") as f:
            path = f.read().strip()
            if os.path.exists(path):
                return path
    except FileNotFoundError:
        pass
    return None
