#!/usr/bin/env python3
"""Twin cipher: 3-char groups (105=3x35, 45=3x15). Brute triple->byte/char mappings,
incl. reversed ('mirror') alphabet, then for onion try base32->.onion."""
import base64, re
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"

def groups(s,n=3): return [s[i:i+n] for i in range(0,len(s),n)]

def val(ch, alpha): return alpha.index(ch) if ch in alpha else -1
def triple_int(t, alpha, base):
    v=0
    for c in t:
        d=val(c,alpha)
        if d<0 or d>=base: return None
        v=v*base+d
    return v

def printable(bs):
    try: txt=bytes(bs).decode("utf-8")
    except: return None
    return txt if all(32<=ord(c)<127 for c in txt) else None

def meaningful(s):
    return any(w in s.lower() for w in ["onion","nightfall","control","hackthe","http","dome",".website",".onion","dpl","deploy","token","runner","portal","mirror","rook","raven"])

alphabets={
 "b36":B36, "b36rev":B36[::-1],
 "b32std":"abcdefghijklmnopqrstuvwxyz234567", "b32rev":"abcdefghijklmnopqrstuvwxyz234567"[::-1],
}

for name,s in [("TOKEN",token),("ONION",onion)]:
    print(f"\n{'='*60}\n{name}  groups={groups(s)[:6]}...\n{'='*60}")
    gs=groups(s)
    for an,alpha in alphabets.items():
        for base in (36,32):
            ints=[triple_int(t,alpha,base) for t in gs]
            if any(v is None for v in ints): continue
            for red,fn in [("%256",lambda v:v%256),("%128",lambda v:v%128),
                           ("%95+32",lambda v:v%95+32),("%94+33",lambda v:v%94+33)]:
                bs=[fn(v) for v in ints]
                txt=printable(bs)
                if txt:
                    tag=" *** " if meaningful(txt) else ""
                    print(f"  [{an} b{base} {red}] {txt}{tag}")
                    # for onion also try base32 of raw bytes
            # also: raw bytes -> base32 (onion address candidate)
            raw=bytes(v%256 for v in ints)
            try:
                b32=base64.b32encode(raw).decode().lower().rstrip("=")
                if meaningful(b32) or name=="ONION":
                    pass
            except: pass

# Also: strip leading digit, treat remaining 2 chars as the data (base36 -> maybe hex-ish)
print("\n--- strip-leading-digit variants ---")
for name,s in [("TOKEN",token),("ONION",onion)]:
    gs=groups(s)
    data_pairs="".join(t[1:] for t in gs)   # 2 chars per group
    print(f"  {name} data(no-lead) [{len(data_pairs)}]: {data_pairs}")
    lead="".join(t[0] for t in gs)
    print(f"  {name} leads: {lead}")
    # try each pair as base36 byte %256 and %128
    pairs=[data_pairs[i:i+2] for i in range(0,len(data_pairs),2)]
    for red,fn in [("%256",lambda v:v%256),("%128",lambda v:v%128),("%95+32",lambda v:v%95+32)]:
        try:
            bs=[fn(int(p,36)) for p in pairs]
            txt=printable(bs)
            if txt: print(f"    pairs b36 {red}: {txt}{' ***' if meaningful(txt) else ''}")
        except: pass
