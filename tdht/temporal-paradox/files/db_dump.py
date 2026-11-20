import sqlite3
c = sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur = c.cursor()
for t, name, sql in cur.execute("SELECT type,name,sql FROM sqlite_master").fetchall():
    print("SCHEMA:", t, name)
    print("   ", sql)
print("\n=== tables ===")
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
for tbl in tables:
    cols = [d[1] for d in cur.execute(f"PRAGMA table_info({tbl})")]
    n = cur.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
    print(f"\n#### {tbl}  ({n} rows)  cols={cols}")
    for row in cur.execute(f"SELECT * FROM {tbl} LIMIT 8"):
        print("   ", row)
