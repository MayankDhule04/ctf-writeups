import sqlite3
c=sqlite3.connect(r'extracted/var/cache/deltaforge/historian_cache.db')
cur=c.cursor()

# device slot offset = (device_time_ns mod 1e9) / 9e6  -> slot index 0..13
rows=list(cur.execute("SELECT asset_tag,seq_no,device_time_ns,gateway_time_ns FROM samples WHERE quality=128 AND seq_no=0"))
recs=[]
for a,s,d,g in rows:
    slot=(d%1000000000)//9000000
    skew=g-d
    gfrac=g%1000000000
    recs.append((slot,a,skew,gfrac,d,g))
recs.sort()
print("slot order:")
for slot,a,skew,gfrac,d,g in recs:
    print(f" slot{slot:2d} {a} skew={skew} gfrac={gfrac}")

skews=[r[2] for r in recs]
gfracs=[r[3] for r in recs]

def out(name, vals):
    bs=bytes(v&0xff for v in vals)
    print(f"{name} hex={bs.hex()} ascii={''.join(chr(x) if 32<=x<127 else '.' for x in bs)}")

print()
out("skew&0xff", skews)
out("skew>>8&0xff",[v>>8 for v in skews])
out("skew//1e6",[v//1000000 for v in skews])
out("gfrac&0xff", gfracs)
out("gfrac//1e6",[v//1000000 for v in gfracs])
out("gfrac mod 95+32",[(v%95)+32 for v in gfracs])
out("skew mod 95+32",[(v%95)+32 for v in skews])
# last 3 digits of skew
out("skew%1000 &0xff",[ (v%1000) for v in skews])
# gfrac last two digits
out("gfrac%100",[v%100 for v in gfracs])
# skew // 1000 mod 256
out("skew//1000",[ (v//1000) for v in skews])
# maybe the byte = (skew mod 1000000)//something
out("(skew%1e6)//4096",[(v%1000000)//4096 for v in skews])
print("\nraw skews:",skews)
print("raw gfracs:",gfracs)
