import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
needles = [b"signal", b"Signal", b"whisper", b"Whisper", b"domectf", b".onion",
           b"signalroom", b"SignalRoom", b"The Signal", b"afterdark", b"after dark"]
CHUNK = 16*1024*1024
overlap = 64
found = {}
with open(f, "rb") as fh:
    off = 0; prev = b""
    while True:
        data = fh.read(CHUNK)
        if not data: break
        buf = prev + data
        for n in needles:
            s = 0
            while True:
                i = buf.find(n, s)
                if i < 0: break
                found.setdefault(n.decode('latin1','replace'), []).append(off-len(prev)+i)
                s = i+1
        prev = buf[-overlap:]
        off += len(data)
for k,v in found.items():
    print(k, len(v), v[:8])
if not found:
    print("NO HITS")
