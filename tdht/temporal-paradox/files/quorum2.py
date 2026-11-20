import json
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'
accepted=[2,3,6,8,9,10]
def parse(rec):
    ln=rec[5]|(rec[6]<<8); i=8; ents={}
    while i<ln-2:
        mid=rec[i]; pl=rec[i+1]; ents[tag_to_mod.get(mid,hex(mid))]=rec[i+2:i+2+pl]; i+=2+pl
    return ents
ents={i:parse(open(f"r9cf/rec{i:02d}.bin","rb").read()) for i in accepted}
ROUTE=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]

def xorbytes(list_of):
    L=max(len(v) for v in list_of); a=bytearray(L)
    for v in list_of:
        for k in range(len(v)): a[k]^=v[k]
    return bytes(a)

def show(tag,bs):
    print(f"{tag}: {bs.hex()}  ascii={''.join(chr(c) if 32<=c<127 else '.' for c in bs)}")

# per module, take DISTINCT values (preserve first-seen order) then XOR
print("=== XOR of DISTINCT share values per module ===")
out=b''
for m in ROUTE:
    seen=[]; 
    for i in accepted:
        v=ents[i].get(m,b'')
        if v not in seen: seen.append(v)
    x=xorbytes(seen) if seen else b''
    out+=x
    show(m,x)
print("\nconcat:",out.hex()); show("ALL",out)

# active lane1 modules only, distinct XOR
ACT=["o4","dx","c7","cf","g8","ml","lc"]
out2=b''
for m in ACT:
    seen=[]
    for i in accepted:
        v=ents[i].get(m,b'')
        if v not in seen: seen.append(v)
    out2+=xorbytes(seen)
print("\nactive distinct concat:",out2.hex()); show("ACT",out2)

# Also: the differences between the two o4 values etc might be text.
