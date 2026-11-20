f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
LFH = b"PK\x03\x04"
EOCD = b"PK\x05\x06"
CENTRAL = b"PK\x01\x02"

CHUNK = 8*1024*1024
overlap = 8
hits = {"LFH": [], "EOCD": [], "CENTRAL": []}
with open(f, "rb") as fh:
    off = 0; prev = b""
    while True:
        data = fh.read(CHUNK)
        if not data: break
        buf = prev + data
        for name, sig in [("LFH", LFH), ("EOCD", EOCD), ("CENTRAL", CENTRAL)]:
            s = 0
            while True:
                i = buf.find(sig, s)
                if i < 0: break
                abs_off = off - len(prev) + i
                hits[name].append(abs_off)
                s = i + 1
        prev = buf[-overlap:]
        off += len(data)

for k, v in hits.items():
    print(k, len(v), v[:20])
