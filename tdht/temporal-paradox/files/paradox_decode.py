import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()

# The two paradox channels
for tag in ["CR9.TEMP.A2","CR9.FLOW.A4"]:
    rows=list(cur.execute("SELECT seq_no,device_time_ns,gateway_time_ns,sensor_value FROM samples WHERE quality=128 AND asset_tag=? ORDER BY seq_no",(tag,)))
    skews=[g-d for (s,d,g,v) in rows]
    print(tag, "skews", skews)
    # local cadence = consecutive deltas
    deltas=[skews[i+1]-skews[i] for i in range(len(skews)-1)]
    print("   deltas", deltas)

# "symbols preserve local cadence; absolute buckets disabled"
# maybe each asset's 6 anomaly skews encode via inter-sample gaps.
# Try: for ALL 14 assets, ordered by seq then asset, take skew deltas mod 256
print("\n=== all-asset local cadence (skew delta within asset) ===")
tags=[r[0] for r in cur.execute("SELECT DISTINCT asset_tag FROM samples ORDER BY asset_tag")]
allbytes=[]
for tag in tags:
    rows=list(cur.execute("SELECT seq_no,device_time_ns,gateway_time_ns FROM samples WHERE quality=128 AND asset_tag=? ORDER BY seq_no",(tag,)))
    sk=[g-d for (s,d,g) in rows]
    d=[(sk[i+1]-sk[i]) for i in range(len(sk)-1)]
    b=[x&0xff for x in d]
    allbytes+=b
    print(tag, bytes(b).hex())
print("concat ascii:", bytes([x for x in allbytes]).decode('latin1'))
