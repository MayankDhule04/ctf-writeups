import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
rows=list(cur.execute("SELECT asset_tag,seq_no,device_time_ns,gateway_time_ns,sensor_value FROM samples WHERE quality=128 ORDER BY gateway_time_ns"))
print("count",len(rows))
print("\n=== RAW full timestamps (transmission order) ===")
for a,s,d,g,v in rows:
    print(f"{a} seq{s:5d} dev={d} gw={g} skew={g-d}")
