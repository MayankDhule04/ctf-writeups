import sqlite3, os, glob

d = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\carved_dbs"
for path in sorted(glob.glob(os.path.join(d, "*.sqlite"))):
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print("="*20, os.path.basename(path), tables, "="*20)
    for t in tables:
        if t == "sqlite_sequence":
            continue
        try:
            cur.execute("SELECT * FROM " + t)
            rows = cur.fetchall()
            cols = [c[0] for c in cur.description]
            print("--", t, cols, "[%d rows]" % len(rows), "--")
            for r in rows:
                print(r)
        except Exception as e:
            print(t, "ERR", e)
    con.close()
    print()
