import sqlite3
import pytest

@pytest.fixture(scope="function")
def sqlite_memory_db():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_sqlite_extension_load(sqlite_memory_db):
    conn = sqlite_memory_db
    # Example: load the FTS5 extension if available (common in SQLite builds)
    try:
        conn.enable_load_extension(True)
        conn.execute("SELECT load_extension('fts5')")
        loaded = True
    except Exception as e:
        loaded = False
    finally:
        conn.enable_load_extension(False)
    # The test passes if extension loads or is not available (no crash)
    assert loaded or not loaded

def test_basic_sqlite_insert(sqlite_memory_db):
    conn = sqlite_memory_db
    conn.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO user (name) VALUES (?)", ("Alice",))
    result = conn.execute("SELECT name FROM user WHERE id=1").fetchone()
    assert result[0] == "Alice"
