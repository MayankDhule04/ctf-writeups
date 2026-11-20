#!/usr/bin/env python3
"""Twin: 3->1 printable char linear map; solve d so the TOKEN is clean [A-Za-z0-9].
Print onion+token candidates for inspection/oracle-testing."""
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"
def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]
ot=trips(onion); tt=trips(token)
alnum=set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")

out=[]
for mirror in (False,True):
    for order in ("abc","cba"):
        vf=(lambda c:(35-B36.index(c))) if mirror else (lambda c:B36.index(c))
        def tv(t):
            v=[vf(c) for c in t]
            return (v[0],v[1],v[2]) if order=="abc" else (v[2],v[1],v[0])
        O=[tv(t) for t in ot]; T=[tv(t) for t in tt]
        for a in range(36):
            for b in range(36):
                for c in range(36):
                    Vt=[a*v0+b*v1+c*v2 for v0,v1,v2 in T]
                    for mod,off in ((95,32),(94,33)):
                        R={v for v in range(mod) if chr(v+off) in alnum}
                        valid=set(range(mod))
                        for q in set(x%mod for x in Vt):
                            valid &= {(r-q)%mod for r in R}
                            if not valid: break
                        for d in valid:
                            ts=''.join(chr((x+d)%mod+off) for x in Vt)
                            Vo=[a*v0+b*v1+c*v2 for v0,v1,v2 in O]
                            os_=''.join(chr((x+d)%mod+off) for x in Vo)
                            out.append((ts,os_,mirror,order,a,b,c,d,mod))

print("candidates:",len(out))
# dedup by token
seen=set()
for ts,os_,mi,o,a,b,c,d,mod in out:
    if ts in seen: continue
    seen.add(ts)
    print(f"  TOKEN={ts}  ONION={os_}  [m={mi} o={o} {a},{b},{c},{d} mod{mod}]")
    if len(seen)>40: print("  ... (more)"); break
