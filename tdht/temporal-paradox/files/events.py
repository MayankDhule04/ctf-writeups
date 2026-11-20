import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
print("=== runtime_events (all) ===")
for row in cur.execute("SELECT event_time_ns,lane,code,detail FROM runtime_events ORDER BY event_time_ns"):
    print(row)
print("\n=== system_info ===")
for row in cur.execute("SELECT * FROM system_info"): print(row)
