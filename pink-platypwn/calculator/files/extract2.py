#!/usr/bin/env python3
import sys, zlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

for fn in ("lib_pink.tns","pink.tns"):
    data = open(os.path.join(HERE,fn),"rb").read()
    print(f"\n===== {fn} ({len(data)} bytes) =====")
    seen=set()
    for start in range(len(data)):
        for wbits in (15,-15,31,47):
            try:
                d=zlib.decompressobj(wbits)
                out=d.decompress(data[start:])+d.flush()
            except Exception:
                continue
            if len(out)<60: continue
            pr=sum(1 for b in out if 9<=b<=13 or 32<=b<=126)/len(out)
            if pr<0.90: continue
            key=out[:40]
            if key in seen: continue
            seen.add(key)
            print(f"\n--- stream start={start} wbits={wbits} outlen={len(out)} printable={pr:.2f} ---")
            print(out.decode("utf-8","replace"))
