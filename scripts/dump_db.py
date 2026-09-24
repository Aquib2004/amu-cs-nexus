import sqlite3
from pathlib import Path

db = Path(r"c:\Users\faizan\Desktop\amu.ai\amu-cs-nexus\backend\amucs_nexus_dev.db")
c = sqlite3.connect(db)
c.row_factory = sqlite3.Row
cur = c.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("DATABASE:", db)
print("TABLES:", tables)
print("=" * 70)

for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    print(f"\n### TABLE: {t}  ({count} rows)")
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print("columns:", cols)
    cur.execute(f"SELECT * FROM {t}")
    for row in cur.fetchall():
        vals = {k: (str(v)[:60] if v is not None else None) for k, v in dict(row).items()}
        print(" -", vals)
