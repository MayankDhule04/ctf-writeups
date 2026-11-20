#!/usr/bin/env python3
import sys, zlib, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

for fn in ("lib_pink.tns","pink.tns"):
    path = os.path.join(HERE, fn)
    data = open(path,"rb").read()
    print(f"\n===== {fn} ({len(data)} bytes) =====")
    # scan for zlib/gzip signatures
    for i in range(len(data)-1):
        two = data[i:i+2]
        if two in (b"\x78\x9c", b"\x78\x01", b"\x78\xda", b"\x78\x5e") or two==b"\x1f\x8b":
            print(f"  signature {two.hex()} at offset {i}")
    # brute every offset, every wbits, accept any sizable output
    best=None
    for start in range(len(data)):
        for wbits in (15,-15,31,47,-9,-10,-11,-12,-13,-14):
            try:
                d=zlib.decompressobj(wbits)
                out=d.decompress(data[start:])+d.flush()
                if len(out)>=80:
                    printable=sum(1 for b in out if 9<=b<=13 or 32<=b<=126)/len(out)
                    if printable>0.85:
                        print(f"  decompress OK start={start} wbits={wbits} len={len(out)} printable={printable:.2f}")
                        open(path+".xml","wb").write(out)
                        best=out; break
            except Exception:
                pass
        if best: break
    if best:
        print(best.decode("utf-8","replace")[:2000])
    else:
        print("  no zlib/deflate decompression found")
