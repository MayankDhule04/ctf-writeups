#!/usr/bin/env python3
"""Twin: test 'byte = 2-of-3 triple chars as base36' formulas vs v3 onion checksum."""
import hashlib, base64
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"
def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]
def dv(c): return B36.index(c)
def mir(v): return 35-v
def v3_ok(b):
    return len(b)==35 and b[34]==3 and hashlib.sha3_256(b".onion checksum"+bytes(b[:32])+b"\x03").digest()[:2]==bytes(b[32:34])
def onion_addr(b): return base64.b32encode(bytes(b)).decode().lower().rstrip("=")+".onion"

ot=trips(onion); tt=trips(token)

# formulas producing a byte from (v0,v1,v2)
def formulas(v):
    v0,v1,v2=v
    m0,m1,m2=mir(v0),mir(v1),mir(v2)
    return {
      "v0*36+v1": v0*36+v1, "v1*36+v2": v1*36+v2, "v0*36+v2": v0*36+v2,
      "v1*36+v0": v1*36+v0, "v2*36+v1": v2*36+v1, "v2*36+v0": v2*36+v0,
      "(v0*36^2+v1*36+v2)%256": (v0*1296+v1*36+v2)%256,
      "(rev)%256": (v2*1296+v1*36+v0)%256,
      "mir:m0*36+m1": m0*36+m1, "mir:m1*36+m2": m1*36+m2, "mir:m0*36+m2": m0*36+m2,
      "mir:(m0*1296+m1*36+m2)%256": (m0*1296+m1*36+m2)%256,
    }

keys=list(formulas((0,0,0)).keys())
for k in keys:
    try:
        bs=[formulas([dv(c) for c in t])[k] for t in ot]
    except: continue
    if all(0<=x<256 for x in bs):
        ok=v3_ok(bs)
        rng=(min(bs),max(bs))
        if ok:
            print(f"*** v3 VALID [{k}]: {onion_addr(bs)}")
        # also show candidates whose last byte is 3 (version) as near-misses
        if bs[34]==3:
            print(f"  near [{k}] ver=3 cksum {'OK' if ok else 'no'} range={rng}")

# If a formula validates, decode token with same formula
print("\n-- token under each formula (printable?) --")
for k in keys:
    try:
        bs=[formulas([dv(c) for c in t])[k] for t in tt]
    except: continue
    if all(0<=x<256 for x in bs):
        try:
            txt=bytes(bs).decode("utf-8")
            if all(32<=ord(c)<127 for c in txt):
                print(f"  [{k}] token -> {txt}")
        except: pass
