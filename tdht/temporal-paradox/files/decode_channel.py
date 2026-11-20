import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()

# Get all quality=128 anomalies grouped by asset
rows=list(cur.execute("SELECT asset_tag,seq_no,device_time_ns,gateway_time_ns FROM samples WHERE quality=128 ORDER BY asset_tag,seq_no"))
from collections import defaultdict
by=defaultdict(list)
for a,s,d,g in rows: by[a].append((s,d,g))

print("=== per-asset anomaly skew profile ===")
for a in sorted(by):
    seqs=by[a]
    skews=[g-d for (s,d,g) in seqs]
    print(f"{a}: n={len(seqs)} skews={skews}")

# The two channels with wild skews carry data. Extract low byte of skew (mod 256) as bytes.
print("\n=== decode attempts ===")
for a in sorted(by):
    seqs=sorted(by[a])
    skews=[g-d for (s,d,g) in seqs]
    lb=bytes([(sk)&0xff for sk in skews])
    print(f"{a} lowbytes: {lb.hex()}  ascii={lb.decode('latin1', 'replace')!r}")
