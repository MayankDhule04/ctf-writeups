#!/usr/bin/env python3
"""Twin cipher — base36-complement (involution) + position-Caesar battery."""
import re
B36="0123456789abcdefghijklmnopqrstuvwxyz"
IDX={c:i for i,c in enumerate(B36)}
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"

def show(label,s):
    hit=[w for w in ["onion","nightfall","control","hackthe","http","dome",".website",".onion","dpl","deploy","token","runner","portal","mirror"] if w in s.lower()]
    mark=" <<<" if hit else ""
    print(f"  [{label}] {s}{(' HITS '+str(hit)) if hit else ''}{mark}")

def b36comp(s):  # v -> 35-v
    return "".join(B36[35-IDX[c]] if c in IDX else c for c in s)
def digcomp(s):  # digit 9-d, letter atbash
    out=[]
    for c in s:
        if c.isdigit(): out.append(str(9-int(c)))
        elif c.isalpha(): out.append(chr(ord('z')-(ord(c)-ord('a'))))
        else: out.append(c)
    return "".join(out)
def caesar36(s,k):
    return "".join(B36[(IDX[c]+k)%36] if c in IDX else c for c in s)
def pos_caesar(s,sign):
    return "".join(B36[(IDX[c]+sign*i)%36] if c in IDX else c for c in s)

for name,S in [("ONION",onion),("TOKEN",token)]:
    print(f"\n==== {name} ====")
    show("b36comp", b36comp(S))
    show("b36comp+rev", b36comp(S)[::-1])
    show("b36comp(rev)", b36comp(S[::-1]))
    show("digcomp", digcomp(S))
    show("digcomp+rev", digcomp(S)[::-1])
    # position caesar
    for sign in (1,-1):
        show(f"posCaesar{sign:+}", pos_caesar(S,sign))
    # fixed caesar sweep - only print readable-ish
    for k in range(1,36):
        r=caesar36(S,k)
        if any(w in r.lower() for w in ["onion","hackthe","dome","dpl","deploy","token","runner","control",".web"]):
            show(f"caesar+{k}", r)

# Also: maybe the token is base36-complement THEN hex/ascii
import binascii
for name,S in [("ONION",onion),("TOKEN",token)]:
    c=b36comp(S)
    print(f"\n{name} b36comp = {c}")
    # try reading the complement as leet
    leet=c.translate(str.maketrans("013457896","oieastgbg"))
    show(f"{name} b36comp-leet", leet)
