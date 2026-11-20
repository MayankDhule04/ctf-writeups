#!/usr/bin/env python3
import sys, zlib, struct, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"c:\Users\mayan\OneDrive\Desktop\ctf\flashback.swf"
raw = open(P,"rb").read()
sig = raw[:3]
print("signature:", sig, "version:", raw[3], "filelen hdr:", struct.unpack("<I",raw[4:8])[0])
if sig == b"CWS":
    body = zlib.decompress(raw[8:])
elif sig == b"FWS":
    body = raw[8:]
else:
    body = raw[8:]
data = raw[:8] + body
print("decompressed body:", len(body), "total:", len(data))
open(r"c:\Users\mayan\OneDrive\Desktop\ctf\flashback_uncompressed.swf","wb").write(b"FWS"+bytes([raw[3]])+struct.pack("<I",len(data))+body)

# pull printable ASCII strings (len>=3)
strings = re.findall(rb"[\x20-\x7e]{3,}", body)
print("\n=== strings (>=3) ===")
for s in strings:
    print(s.decode("latin1"))
