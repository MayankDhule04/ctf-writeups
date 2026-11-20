#!/usr/bin/env python3
"""New model: the two 'twin' strings combine. Test onion (A) vs token (B, cycled) under
base36 add/sub/xor (B forward & reversed), and the group-sep streams combining."""
import base64, re
A="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
B="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"
B36="0123456789abcdefghijklmnopqrstuvwxyz"
def v(c): return B36.index(c)
def ch(n): return B36[n%36]

def interesting(s):
    low=s.lower()
    return any(w in low for w in ["onion","hackthe","control","http","nightfall","lantern","dome",".web","dpl","deploy","runner","portal"])

def report(label,s):
    tag=" <<<" if interesting(s) else ""
    print(f"  [{label}] {s}{tag}")

print("=== A combined with B (cycled) ===")
for Bv,blab in [(B,"B"),(B[::-1],"revB")]:
    for op,olab in [((lambda a,b:(a-b)%36),"sub"),((lambda a,b:(a+b)%36),"add"),
                    ((lambda a,b:(b-a)%36),"rsub"),((lambda a,b:(v2:=a^b)%36 if a^b<36 else (a^b)%36),"xor")]:
        out="".join(ch(op(v(A[i]),v(Bv[i%len(Bv)]))) for i in range(len(A)))
        report(f"A {olab} {blab}", out)

print("\n=== B combined with A (cycled, first 45) ===")
for Av,alab in [(A,"A"),(A[::-1],"revA")]:
    for op,olab in [((lambda a,b:(a-b)%36),"sub"),((lambda a,b:(a+b)%36),"add"),((lambda a,b:(b-a)%36),"rsub")]:
        out="".join(ch(op(v(B[i]),v(Av[i%len(Av)]))) for i in range(len(B)))
        report(f"B {olab} {alab}", out)

# group-level: combine the two data streams (sep stripped) if same length-ish
def trips(s): return [s[i:i+3] for i in range(0,len(s),3)]
Adata="".join(t[1:] for t in trips(A))  # 70
Bdata="".join(t[1:] for t in trips(B))  # 30
Aleads="".join(t[0] for t in trips(A))  # 35
Bleads="".join(t[0] for t in trips(B))  # 15
print("\n=== data/lead streams ===")
print(f"  Adata({len(Adata)}): {Adata}")
print(f"  Bdata({len(Bdata)}): {Bdata}")
print(f"  Aleads({len(Aleads)}): {Aleads}")
print(f"  Bleads({len(Bleads)}): {Bleads}")

# combine Adata with Bleads/Bdata cycled
for key,klab in [(Bdata,"Bdata"),(Bleads,"Bleads"),(Aleads,"Aleads")]:
    out="".join(ch((v(Adata[i])-v(key[i%len(key)]))%36) for i in range(len(Adata)))
    report(f"Adata sub {klab}", out)
    out="".join(ch((v(Adata[i])+v(key[i%len(key)]))%36) for i in range(len(Adata)))
    report(f"Adata add {klab}", out)

# sep stream as shift key for data (per-group): data pair shifted by that group's sep
print("\n=== per-group: shift data pair by group's sep ===")
for s,slab in [(A,"A"),(B,"B")]:
    T=trips(s)
    for sign in (1,-1):
        out="".join(ch((v(c)+sign*int(t[0]))%36) for t in T for c in t[1:])
        report(f"{slab} datashift({sign:+}sep)", out)
