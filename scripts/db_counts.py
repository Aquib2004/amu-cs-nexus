import sqlite3

db = r"c:\Users\faizan\Desktop\amu.ai\amu-cs-nexus\backend\amucs_nexus_dev.db"
c = sqlite3.connect(db)
for t in ["documents", "chunks", "notices", "faculties", "programs",
          "laboratories", "research_projects", "staff_members", "ingestion_log"]:
    n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    emb = 0
    if t == "chunks":
        emb = c.execute("SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL").fetchone()[0]
    print(f"{t:18} rows={n}" + (f"  embedded={emb}" if t == "chunks" else ""))
c.close()