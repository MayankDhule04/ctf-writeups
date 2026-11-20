import os,json
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'

accepted=[2,3,6,8,9,10]
recs={}
for i in accepted:
    recs[i]=open(f"r9cf/rec{i:02d}.bin","rb").read()

# 1) XOR all accepted full records (they're all 98 bytes)
from functools import reduce
x=bytearray(98)
for i in accepted:
    for j in range(98):
        x[j]^=recs[i][j]
print("XOR all 6 accepted (full):", bytes(x).hex())
def show(bs):
    print("  ascii:", ''.join(chr(c) if 32<=c<127 else '.' for c in bs))
show(x)

# 2) parse entries, XOR per-module payloads across shares, in route-table (module index) order
def parse(rec):
    ln=rec[5]|(rec[6]<<8); i=8; ents={}
    while i<ln-2:
        mid=rec[i]; pl=rec[i+1]; ents[tag_to_mod.get(mid,hex(mid))]=rec[i+2:i+2+pl]; i+=2+pl
    return ents

ents={i:parse(recs[i]) for i in accepted}
# module route order per binary name table
ROUTE=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]
print("\n=== per-module XOR across the 6 shares ===")
out=b''
for m in ROUTE:
    vals=[ents[i].get(m,b'') for i in accepted]
    L=max(len(v) for v in vals)
    acc=bytearray(L)
    for v in vals:
        for k in range(len(v)): acc[k]^=v[k]
    print(f"{m}: shares={[v.hex() for v in vals]} XOR={bytes(acc).hex()}")
    out+=bytes(acc)
print("\nconcat XOR:", out.hex()); show(out)

# 3) lane1 active modules only (o4,dx,c7,cf,g8,ml,lc), XOR
ACT=["o4","dx","c7","cf","g8","ml","lc"]
out2=b''
for m in ACT:
    vals=[ents[i].get(m,b'') for i in accepted]
    L=max(len(v) for v in vals); acc=bytearray(L)
    for v in vals:
        for k in range(len(v)): acc[k]^=v[k]
    out2+=bytes(acc)
print("\nactive-only concat XOR:", out2.hex()); show(out2)
