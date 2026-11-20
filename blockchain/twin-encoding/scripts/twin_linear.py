#!/usr/bin/env python3
"""Rigorous: assume 3-char groups -> byte = (a*v0+b*v1+c*v2+d) mod 256.
Brute (a,b,c), solve d so last byte=version 3, validate v3 .onion SHA3 checksum."""
import hashlib, base64, itertools
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"

def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]
def v3_ok(b):
    if len(b)!=35 or b[34]!=3: return False
    return hashlib.sha3_256(b".onion checksum"+bytes(b[:32])+b"\x03").digest()[:2]==bytes(b[32:34])
def addr(b): return base64.b32encode(bytes(b)).decode().lower().rstrip("=")+".onion"

ot=trips(onion); tt=trips(token)

# value functions
def valfn(mirror):
    return (lambda c: (35-B36.index(c)) if mirror else B36.index(c))

hits=[]
configs=[]
for mirror in (False,True):
    for order in ("abc","cba"):
        vf=valfn(mirror)
        # precompute (v0,v1,v2) per triple with chosen order
        def vget(t):
            vs=[vf(ch) for ch in t]
            return (vs[0],vs[1],vs[2]) if order=="abc" else (vs[2],vs[1],vs[0])
        O=[vget(t) for t in ot]
        last=O[-1]
        for a in range(36):
            for b in range(36):
                for c in range(36):
                    d=(3-(a*last[0]+b*last[1]+c*last[2]))%256
                    bs=[(a*v0+b*v1+c*v2+d)%256 for (v0,v1,v2) in O]
                    if bs[34]!=3: continue
                    if v3_ok(bs):
                        hits.append((mirror,order,a,b,c,d))
                        print(f"*** HIT mirror={mirror} order={order} a={a} b={b} c={c} d={d}")
                        print("    ONION:", addr(bs))
                        # decode token same mapping
                        T=[vget(t) for t in tt]
                        tb=[(a*v0+b*v1+c*v2+d)%256 for (v0,v1,v2) in T]
                        try:
                            tx=bytes(tb).decode("utf-8")
                            print("    TOKEN bytes->ascii:", tx)
                        except:
                            print("    TOKEN bytes(hex):", bytes(tb).hex())
                            print("    TOKEN b32:", base64.b32encode(bytes(tb)).decode().lower().rstrip("="))
print("\nhits:", hits if hits else "NONE (mapping not linear-mod256 over base36 values)")
