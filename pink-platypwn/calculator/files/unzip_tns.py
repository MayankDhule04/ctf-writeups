#!/usr/bin/env python3
import sys, os, struct, zlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

def parse_local_headers(data):
    out = []
    i = 0
    while True:
        sig = data.find(b"PK\x03\x04", i)
        if sig < 0: break
        hdr = data[sig:sig+30]
        if len(hdr) < 30: break
        (_, ver, flags, method, mtime, mdate, crc, csize, usize, nlen, elen) = struct.unpack("<IHHHHHIIIHH", hdr)
        name = data[sig+30:sig+30+nlen].decode("latin1")
        dstart = sig+30+nlen+elen
        comp = data[dstart:dstart+csize] if csize else None
        out.append((name, method, csize, usize, crc, dstart, comp))
        i = sig+4
    return out

for fn in ("lib_pink.tns","pink.tns"):
    data = open(os.path.join(HERE,fn),"rb").read()
    print(f"\n===== {fn} =====")
    for name, method, csize, usize, crc, dstart, comp in parse_local_headers(data):
        print(f"\n--- {name}  method={method} csize={csize} usize={usize} dstart={dstart} ---")
        raw = b""
        if comp is not None:
            if method == 0:
                raw = comp
            else:
                try:
                    raw = zlib.decompress(comp, -15)
                except Exception as e:
                    # fallback: inflate as much as possible
                    d = zlib.decompressobj(-15)
                    try: raw = d.decompress(data[dstart:]) + d.flush()
                    except Exception as e2: print("  inflate fail", e, e2)
        try:
            print(raw.decode("utf-8"))
        except Exception:
            print(repr(raw[:400]))
        open(os.path.join(HERE, fn.replace('.tns','')+"__"+name.replace('/','_')), "wb").write(raw)
