import os, json
tag_to_mod={int(k):v for k,v in json.loads(open('tag_map.json').read()).items()}
tag_to_mod[0x84]='dx'
ROUTE=["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]
accepted=[2,3,6,8,9,10]

def parse(rec):
    ln=rec[5]|(rec[6]<<8); i=8; ents=[]; order=[]
    while i<ln-2:
        mid=rec[i]; pl=rec[i+1]; ents.append((tag_to_mod.get(mid,hex(mid)),rec[i+2:i+2+pl])); i+=2+pl
    return ents

recs={i:open(f"r9cf/rec{i:02d}.bin","rb").read() for i in accepted}

def lane1_transform(data):
    # state ^= sym, frame edge 64
    state=0; out=bytearray()
    for i,sym in enumerate(data):
        state ^= sym
        out.append(state)
    return bytes(out)

def lane0_transform(data, mask=0xff):
    state=0; out=bytearray()
    for sym in data:
        state=(state+sym)&mask
        out.append(state)
    return bytes(out)

def hexcheck(bs):
    s=bs.hex()
    return s

# Approach A: run transform over each record body (from +8, excluding trailing crc)
for i in accepted:
    rec=recs[i]; ln=rec[5]|(rec[6]<<8)
    body=rec[8:ln-2]
    t1=lane1_transform(body); t0=lane0_transform(body)
    print(f"rec{i:02d} body[{len(body)}]")
    # look at final state bytes / any 14-byte window that's printable
    print("   lane1 final state:", hex(t1[-1]), "lane0 final:", hex(t0[-1]))

# Approach B: The 'sym' are the module payloads in ROUTE order (canonical), concatenated.
def canonical_payload(rec):
    ents=dict(parse(rec))
    out=b''
    for m in ROUTE:
        out+=ents.get(m,b'')
    return out

print("\n=== canonical payload per record + lane1 xor-scan state ===")
for i in accepted:
    cp=canonical_payload(recs[i])
    t1=lane1_transform(cp)
    print(f"rec{i:02d} canon[{len(cp)}]={cp.hex()}")
