import sqlite3, os, re
DB=r'extracted/var/cache/deltaforge/historian_cache.db'
c=sqlite3.connect(DB); cur=c.cursor()

print("=== retired_lane_profiles ===")
try:
    for row in cur.execute("SELECT slot,label,blob,residue FROM retired_lane_profiles ORDER BY slot"):
        slot,label,blob,res=row
        bl = blob.hex() if isinstance(blob,(bytes,bytearray)) else blob
        rs = res.hex() if isinstance(res,(bytes,bytearray)) else res
        print(f"slot={slot} label={label!r}")
        print(f"   blob({len(blob) if blob else 0})={bl}")
        print(f"   residue({len(res) if res else 0})={rs}")
except Exception as e:
    print("ERR", e)

print("\n=== all tables ===")
for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(" ", t[0])

# Look for encoder_crash.fragment and .gdb_history in extracted tree
print("\n=== search extracted tree ===")
for root,dirs,files in os.walk('extracted'):
    for f in files:
        if 'crash' in f or 'gdb' in f or 'fragment' in f or f.endswith('.cal'):
            print(os.path.join(root,f))
