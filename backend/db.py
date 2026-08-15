import sqlite3
from pathlib import Path
DB = Path(__file__).parent / "scamshield.db"
def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, input_type TEXT NOT NULL, preview TEXT NOT NULL, score INTEGER NOT NULL, level TEXT NOT NULL, category TEXT NOT NULL)")
    return c
def add(kind, preview, score, level, category):
    c=conn(); c.execute("INSERT INTO scans (input_type,preview,score,level,category) VALUES (?,?,?,?,?)",(kind,preview[:180],score,level,category)); c.commit(); c.close()
def history():
    c=conn(); rows=[dict(r) for r in c.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 50")]; c.close(); return rows
def clear():
    c=conn(); c.execute("DELETE FROM scans"); c.commit(); c.close()
