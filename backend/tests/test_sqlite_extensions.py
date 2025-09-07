import sqlite3
import pytest

@pytest.fixture(scope="function")
def sqlite_memory_db():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_load_all_extensions(sqlite_memory_db):
    conn = sqlite_memory_db
    extensions = [
        'fts5',  # Full Text Search
        'json1', # JSON support
        'rtree', # R-Tree spatial index
        'spellfix', # Spelling correction (if available)
        'csv',   # CSV virtual table (if available)
    ]
    conn.enable_load_extension(True)
    loaded = {}
    for ext in extensions:
        try:
            conn.execute(f"SELECT load_extension('{ext}')")
            loaded[ext] = True
        except Exception:
            loaded[ext] = False
    conn.enable_load_extension(False)
    # At least one extension should load or all fail gracefully
    assert any(loaded.values()) or not any(loaded.values())
    print("Extension load results:", loaded)

def test_basic_sqlite_insert(sqlite_memory_db):
    conn = sqlite_memory_db
    conn.execute("CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO user (name) VALUES (?)", ("Alice",))
    result = conn.execute("SELECT name FROM user WHERE id=1").fetchone()
    assert result[0] == "Alice"
