import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.local/share/dotInstaller/dotinstaller.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS installed_apps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    type TEXT,
    install_date TEXT
);
"""

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)
        conn.commit()

def register_install(name, file_path, type_):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO installed_apps (name, file_path, type, install_date) VALUES (?, ?, ?, ?)",
            (name, file_path, type_, datetime.now().isoformat())
        )
        conn.commit()

def is_installed(file_path):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id FROM installed_apps WHERE file_path = ?",
            (file_path,)
        )
        return cur.fetchone() is not None

def list_installed():
    with get_conn() as conn:
        cur = conn.execute("SELECT id, name, file_path, type, install_date FROM installed_apps ORDER BY install_date DESC")
        return cur.fetchall()

def get_app_details(app_id):
    with get_conn() as conn:
        cur = conn.execute("SELECT id, name, file_path, type, install_date FROM installed_apps WHERE id = ?", (app_id,))
        return cur.fetchone()

def remove_app(app_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM installed_apps WHERE id = ?", (app_id,))
        conn.commit() 