import re
b=open(r"Temporal Paradox/gateway_snapshot.img","rb").read()

# Carve the whole SQLite db out of the image and open it to recover dropped table via page scan.
# DB header 'SQLite format 3' at 0xa22000
db_off=0xa22000
# size: read page size (bytes 16-17 BE) and page count (28-31 BE)
hdr=b[db_off:db_off+100]
pgsz=int.from_bytes(hdr[16:18],'big')
pgcnt=int.from_bytes(hdr[28:32],'big')
print("pgsz",pgsz,"pgcnt",pgcnt,"dbsize",pgsz*pgcnt)
dbimg=b[db_off:db_off+pgsz*pgcnt]
open("carved.db","wb").write(dbimg)

# The extracted historian_cache.db is the LIVE (post-drop) db. The image copy at 0xa22000
# may be an earlier snapshot still containing retired_lane_profiles. Try opening carved.db.
import sqlite3
try:
    c=sqlite3.connect("carved.db"); cur=c.cursor()
    print("tables:", [r[0] for r in cur.execute("SELECT name FROM sqlite_master")])
    try:
        for row in cur.execute("SELECT slot,label,quote(blob),quote(residue) FROM retired_lane_profiles"):
            print("PROFILE", row[0], row[1], row[2][:80] if row[2] else None, "res=",row[3][:120] if row[3] else None)
    except Exception as e:
        print("query err", e)
except Exception as e:
    print("open err", e)

# regardless, scan raw db pages for freeblock/overflow with profile data.
# Look for label-like text 'gen' 'newest' 'current' followed by blobs, plus 'HTF' inside db region only
dbregion=dbimg
print("HTF in db region:", [hex(db_off+m.start()) for m in re.finditer(rb'HTF', dbregion)])
