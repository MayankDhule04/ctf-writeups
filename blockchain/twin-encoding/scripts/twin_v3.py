#!/usr/bin/env python3
"""Twin cipher: 3 chars -> 1 byte (onion 105=3x35 bytes = v3 onion). Brute the
triple->byte mapping and validate with the v3 .onion checksum oracle."""
import hashlib, base64, itertools
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"

def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]

def v3_ok(b):
    if len(b)!=35 or b[34]!=3: return False
    h=hashlib.sha3_256(b".onion checksum"+bytes(b[:32])+bytes([3])).digest()
    return h[:2]==bytes(b[32:34])

def to_onion(b):
    return base64.b32encode(bytes(b)).decode().lower().rstrip("=")+".onion"

ot=trips(onion); tt=trips(token)
print(f"onion {len(ot)} triples, token {len(tt)} triples")

def ti(t, alpha, base, rev=False):
    tt=t[::-1] if rev else t
    v=0
    for c in tt:
        if c not in alpha[:base]: return None
        v=v*base+alpha.index(c)
    return v

found=[]
alphabets={"b36":B36,"b36rev":B36[::-1]}
for an,alpha in alphabets.items():
    for base in (36,):
        for rev in (False,True):
            ints=[ti(t,alpha,base,rev) for t in ot]
            if any(v is None for v in ints): continue
            # try linear reductions: byte=(int+off)%256, byte=int%256, byte=(int*k)%256
            for off in range(0,256,1):
                b=[(v+off)%256 for v in ints]
                if v3_ok(b):
                    found.append((an,base,rev,"+%d"%off)); print(f"  HIT {an} base{base} rev={rev} off={off}: {to_onion(b)}")
            for k in range(1,256):
                b=[(v*k)%256 for v in ints]
                if v3_ok(b):
                    found.append((an,base,rev,"*%d"%k)); print(f"  HIT {an} base{base} rev={rev} mul={k}: {to_onion(b)}")

# weighted-sum mappings: byte = (a*c0 + b*c1 + c*c2) % 256 over base36 digit values
def dv(c): return B36.index(c) if c in B36 else -1
odigs=[[dv(c) for c in t] for t in ot]
if all(all(d>=0 for d in t) for t in odigs):
    import itertools as it
    print("brute weighted sums a*c0+b*c1+c*c2 (+off) % 256 ...")
    rng=range(0,36)
    for a in rng:
        for b_ in rng:
            for c in rng:
                bytes_=[(a*t[0]+b_*t[1]+c*t[2])%256 for t in odigs]
                # quick pre-check version byte
                if bytes_[34]!=3: continue
                if v3_ok(bytes_):
                    print(f"  *** WEIGHTED a={a} b={b_} c={c}: {to_onion(bytes_)}")
                    found.append(("weighted",a,b_,c))
    print("weighted brute done")

print("\nfound:", found)
