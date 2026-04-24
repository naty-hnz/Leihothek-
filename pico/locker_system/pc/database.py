import sqlite3

DB_FILE = "lockers.db"

def get_db():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS lockers (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    UNIQUE,
        tag_id      TEXT,
        expected_g  REAL    DEFAULT 0,
        tolerance_g REAL    DEFAULT 30,
        current_g   REAL    DEFAULT 0,
        status      TEXT    DEFAULT 'CLOSED'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp  TEXT,
        locker     TEXT,
        event      TEXT,
        tag_id     TEXT,
        weight_g   REAL,
        expected_g REAL,
        result     TEXT
    )''')
    conn.commit()
    conn.close()

# ─── Lockers ─────────────────────────────────────────────────────────────────

def get_all_lockers():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, tag_id, expected_g, tolerance_g, current_g, status FROM lockers ORDER BY name")
    rows = [_row_to_locker(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_locker_by_tag(tag_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, tag_id, expected_g, tolerance_g, current_g, status FROM lockers WHERE tag_id = ?", (str(tag_id),))
    row = c.fetchone()
    conn.close()
    return _row_to_locker(row) if row else None

def get_locker_by_id(locker_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, tag_id, expected_g, tolerance_g, current_g, status FROM lockers WHERE id = ?", (locker_id,))
    row = c.fetchone()
    conn.close()
    return _row_to_locker(row) if row else None

def add_locker(name, tag_id, expected_g, tolerance_g):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO lockers (name, tag_id, expected_g, tolerance_g) VALUES (?, ?, ?, ?)",
              (name, str(tag_id), float(expected_g), float(tolerance_g)))
    conn.commit()
    conn.close()

def update_locker_fields(locker_id, **kwargs):
    conn = get_db()
    c = conn.cursor()
    for key, val in kwargs.items():
        c.execute(f"UPDATE lockers SET {key} = ? WHERE id = ?", (val, locker_id))
    conn.commit()
    conn.close()

def delete_locker(locker_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM lockers WHERE id = ?", (locker_id,))
    conn.commit()
    conn.close()

def _row_to_locker(r):
    return {
        "id": r[0], "name": r[1], "tag_id": r[2],
        "expected": r[3], "tolerance": r[4],
        "current": r[5], "status": r[6],
    }

# ─── Events ───────────────────────────────────────────────────────────────────

def log_event(locker_name, event, tag_id=None, weight=None, expected=None, result=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO events (timestamp, locker, event, tag_id, weight_g, expected_g, result)
                 VALUES (datetime('now','localtime'), ?, ?, ?, ?, ?, ?)''',
              (locker_name, event, tag_id, weight, expected, result))
    conn.commit()
    conn.close()

def get_events(limit=100):
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT timestamp, locker, event, tag_id, weight_g, expected_g, result
                 FROM events ORDER BY id DESC LIMIT ?""", (limit,))
    rows = [{"time": r[0], "locker": r[1], "event": r[2], "tag_id": r[3],
             "weight": r[4], "expected": r[5], "result": r[6]} for r in c.fetchall()]
    conn.close()
    return rows
