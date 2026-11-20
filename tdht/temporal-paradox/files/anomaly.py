import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
print("=== quality=128 rows (the 84 anomalies) ===")
rows=list(cur.execute("SELECT id,asset_tag,seq_no,device_time_ns,gateway_time_ns,sensor_value,quality FROM samples WHERE quality=128 ORDER BY gateway_time_ns"))
print("count",len(rows))
for r in rows[:90]:
    dt=r[4]-r[3]  # gateway - device skew
    print(r[1], "seq",r[2], "skew",dt, "val",r[5])
