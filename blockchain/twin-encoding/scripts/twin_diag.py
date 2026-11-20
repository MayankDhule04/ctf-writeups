#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ctf-tool"))
onion="5ec6a81xr14i50w1m31e51pv58l5ow6j65bn5ki1gk6nd5ws5jp53g6536lu69v64m1dx6ci67o6i31rd58h5ck1ei59551q5wu5gv5sf"
token="14p4wn54k1dy1b71tt1n751s1kf67950y56c65q6ag680"

for name,s in [("onion",onion),("token",token)]:
    chars=sorted(set(s))
    print(f"\n{name}: len={len(s)}")
    print(f"  unique chars ({len(chars)}): {''.join(chars)}")
    digs=sorted(set(c for c in s if c.isdigit()))
    lets=sorted(set(c for c in s if c.isalpha()))
    print(f"  digits used ({len(digs)}): {''.join(digs)}")
    print(f"  letters used ({len(lets)}): {''.join(lets)}")
    print(f"  missing digits: {''.join(d for d in '0123456789' if d not in digs)}")
    print(f"  missing letters: {''.join(c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in lets)}")
    # char counts
    from collections import Counter
    print(f"  top counts: {Counter(s).most_common(8)}")

# ctf-tool analyzers
try:
    from ctf_tool import crypto as C
    for name,s in [("onion",onion),("token",token)]:
        print(f"\n=== analyze_cipher({name}) ===")
        try: print(" ", C.analyze_cipher(s))
        except Exception as e: print("  err", e)
        print(f"=== try_all_encodings({name}) ===")
        try:
            for r in C.try_all_encodings(s): print("  ", str(r)[:200])
        except Exception as e: print("  err", e)
except Exception as e:
    print("tool import err:", e)

# extra bases
import base64
for name,s in [("onion",onion),("token",token)]:
    print(f"\n--- extra base decodes {name} ---")
    for fn,lbl in [(base64.a85decode,"a85"),(base64.b85decode,"b85")]:
        for cand in (s, s.upper()):
            try:
                d=fn(cand); print(f"  {lbl}: {d[:60]!r}")
            except Exception: pass
