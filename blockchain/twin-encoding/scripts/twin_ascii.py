#!/usr/bin/env python3
"""Twin: 3 chars -> 1 printable char via linear map. Fast d-intersection.
Filter: onion decodes to a hostname (printable hostname chars, contains a keyword)."""
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"
def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]
ot=trips(onion); tt=trips(token)
allowed=set("abcdefghijklmnopqrstuvwxyz0123456789.-:/_")
KW=("onion","hackthe","http","control","nightfall","lantern",".web","dome")

def vfns():
    for mirror in (False,True):
        for order in ("abc","cba"):
            def f(c,mirror=mirror): return (35-B36.index(c)) if mirror else B36.index(c)
            yield mirror,order,f

hits=0
for mirror,order,vf in vfns():
    def tv(t):
        v=[vf(c) for c in t]
        return (v[0],v[1],v[2]) if order=="abc" else (v[2],v[1],v[0])
    O=[tv(t) for t in ot]; T=[tv(t) for t in tt]
    for a in range(36):
        for b in range(36):
            for c in range(36):
                Vo=[a*v0+b*v1+c*v2 for v0,v1,v2 in O]
                for mod,off in ((95,32),(128,0)):
                    R={v for v in range(mod) if chr(v+off) in allowed}
                    # valid d so every onion char is hostname-allowed
                    valid=set(range(mod))
                    for q in set(x%mod for x in Vo):
                        valid &= {(r-q)%mod for r in R}
                        if not valid: break
                    for d in valid:
                        os_=''.join(chr((x+d)%mod+off) for x in Vo)
                        if any(k in os_ for k in KW):
                            Vt=[a*v0+b*v1+c*v2 for v0,v1,v2 in T]
                            ts_=''.join(chr((x+d)%mod+off) for x in Vt)
                            print(f"[m={mirror} o={order} a={a} b={b} c={c} d={d} mod={mod}]")
                            print("  ONION:",os_)
                            print("  TOKEN:",ts_)
                            hits+=1
print("\nhits:",hits)
