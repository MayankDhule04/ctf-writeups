import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()
rows=list(cur.execute("SELECT asset_tag,seq_no,device_time_ns,gateway_time_ns,sensor_value FROM samples WHERE quality=128 ORDER BY gateway_time_ns"))
print("n",len(rows))
# order by gateway time (transmission order). extract bytes several ways.
skews=[g-d for (a,s,d,g,v) in rows]
def show(name, bs):
    try: asc=bytes(bs).decode('latin1')
    except: asc=''
    print(f"{name}: {bytes(bs).hex()}  | {asc!r}")
show("skew&0xff", [sk&0xff for sk in skews])
show("skew mod 95 +32", [(sk%95)+32 for sk in skews])
show("(skew//1e6)&0xff", [int(abs(sk)//1000000)&0xff for sk in skews])
show("(skew//1000)&0xff", [int(abs(sk)//1000)&0xff for sk in skews])
# device_time low byte
show("dev&0xff", [d&0xff for (a,s,d,g,v) in rows])
show("gw&0xff", [g&0xff for (a,s,d,g,v) in rows])
# nanosecond sub-ms part of device_time
show("dev%1000", [ (d%1000)&0xff for (a,s,d,g,v) in rows])
# order by (seq_no, asset) instead
rows2=sorted(rows,key=lambda r:(r[1],r[0]))
show("byseq dev&0xff", [d&0xff for (a,s,d,g,v) in rows2])
show("byseq skew&0xff", [((g-d)&0xff) for (a,s,d,g,v) in rows2])
