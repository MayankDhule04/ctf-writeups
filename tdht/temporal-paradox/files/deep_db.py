import sqlite3, binascii
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
# full runtime_events, look for egress / transfer / cipher / key
print("=== events with egress/cipher/key/transfer/mirror ===")
for row in cur.execute("SELECT event_time_ns,lane,code,detail FROM runtime_events ORDER BY event_time_ns"):
    d=(row[3] or "")
    print(row)
# any blob columns? check samples value distribution, and look for a table with hex/base64
print("\n=== system_info full ===")
for r in cur.execute("SELECT * FROM system_info"): print(r)
# sample rows count & asset tags
print("\n=== distinct asset_tags ===")
for r in cur.execute("SELECT asset_tag,count(*) FROM samples GROUP BY asset_tag"): print(r)
# the 79156 samples: sensor_value could encode bytes. Check range & quality values
print("\n=== quality distinct ===")
for r in cur.execute("SELECT quality,count(*) FROM samples GROUP BY quality"): print(r)
print("\n=== seq_no range ===")
for r in cur.execute("SELECT min(seq_no),max(seq_no),count(distinct seq_no) FROM samples"): print(r)
