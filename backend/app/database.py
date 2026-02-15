"""
SnapLens — Database Connection

Handles SQLite connection and table initialization.

Why SQLite for MVP?
- Zero setup: no external database server needed
- File-based: the entire DB is one file (snaplens.db)
- Built into Python: no extra package required
- Easy to upgrade to PostgreSQL later if the product scales

Architecture note:
  We use Python's built-in `sqlite3` module directly.
  For a larger app, you'd use an ORM like SQLAlchemy.
  But for an MVP, raw SQL keeps things simple and teaches you how databases actually work.
"""

import os
import sqlite3

# Database file lives in the backend directory
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "snaplens.db")


def get_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.

    Row factory = sqlite3.Row makes rows behave like dictionaries,
    so you can access columns by name: row["category"] instead of row[1].
    This is a professional practice that makes code more readable.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initialize the database — create the items table if it doesn't exist.

    This runs once when the server starts.
    'IF NOT EXISTS' means it won't crash if the table already exists.

    Schema design decisions:
    - id: INTEGER PRIMARY KEY with AUTOINCREMENT → unique item ID
    - category: what type of item (task, note, reminder, expense, link)
    - title: short title generated from the screenshot text
    - summary: brief description of the content
    - key_detail: extracted detail (date, amount, URL) — can be NULL
    - extracted_text: full OCR text — useful for search later
    - suggested_action: what the AI suggested doing
    - created_at: auto-filled timestamp for sorting
    """
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            key_detail TEXT,
            extracted_text TEXT,
            suggested_action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
