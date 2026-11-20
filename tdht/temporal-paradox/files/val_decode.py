import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
rows=list(cur.execute("SELECT asset_tag,seq_no,gateway_time_ns,sensor_value FROM samples WHERE quality=128 ORDER BY gateway_time_ns"))
# low 7 fractional digits
def frac7(v):
    s=f"{v:.7f}".split('.')[1]
    return int(s)
vals=[frac7(r[3]) for r in rows]
print("frac7 &0xff:", bytes([x&0xff for x in vals]).hex())
print("frac7 mod95+32:", ''.join(chr((x%95)+32) for x in vals))
# last 2 digits of the 7-decimal fraction
b2=[frac7(r[3])%100 for r in rows]
print("last2:", b2)
# compare each anomaly value to the 'normal' baseline (median of quality=192 for that asset) -> local cadence
import statistics
base={}
for tag in set(r[0] for r in rows):
    nv=[x[0] for x in cur.execute("SELECT sensor_value FROM samples WHERE quality=192 AND asset_tag=? LIMIT 200",(tag,))]
    base[tag]=statistics.median(nv)
diffs=[(r[3]-base[r[0]]) for r in rows]
print("\nvalue diffs from baseline (first 30):")
for r,d in list(zip(rows,diffs))[:30]:
    print(f"  {r[0]} seq{r[1]} val{r[3]} diff{d:.5f}")
