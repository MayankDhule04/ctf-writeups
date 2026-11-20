import sqlite3, glob, os, re

d=r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\carved_dbs"
pat=re.compile(r'archive|inventory|t-?484|signal|nightfall|internal|artifact|/api/|forwarded|x-real', re.I)
for path in sorted(glob.glob(os.path.join(d,"*.sqlite"))):
    con=sqlite3.connect(path); cur=con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for (t,) in cur.fetchall():
        if t=="sqlite_sequence": continue
        try:
            cur.execute(f"SELECT * FROM {t}")
            cols=[c[0] for c in cur.description]; rows=cur.fetchall()
        except Exception: continue
        for r in rows:
            s=" | ".join(str(x) for x in r)
            if pat.search(s):
                print(f"[{os.path.basename(path)}:{t}] {s[:400]}")
    con.close()
