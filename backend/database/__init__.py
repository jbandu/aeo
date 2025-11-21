import sqlite3
import os
from pathlib import Path

DATABASE_PATH = os.getenv("DATABASE_PATH", "aeo_platform.db")

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_database():
    """Initialize the database with schema."""
    schema_path = Path(__file__).parent / "schema.sql"

    conn = get_db_connection()
    try:
        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        conn.executescript(schema_sql)
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

def get_db():
    """Generator function for database connections (FastAPI dependency)."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
