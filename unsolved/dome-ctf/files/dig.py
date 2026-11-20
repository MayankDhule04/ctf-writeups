import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
USERDATA_OFF = 504365056
USERDATA_LEN = (3887070-985088+1)*512

leads = [b"messages.db", b"conversation", b"vyrqelith", b"pixelfeed",
         b"firefox", b"places.sqlite", b"history", b"bookmark",
         b"cloudsync", b"drive", b"http://", b"https://",
         b"onion", b"nightlens", b"Operation", b"Nightfall",
         b"recovered", b"recovery", b"deleted"]

CHUNK = 8*1024*1024
overlap = 512
found = {}
with open(f, "rb") as fh:
    fh.seek(USERDATA_OFF)
    off = 0; prev = b""
    while off < USERDATA_LEN:
        data = fh.read(min(CHUNK, USERDATA_LEN-off))
        if not data: break
        buf = prev + data
        for kw in leads:
            s = 0
            while True:
                i = buf.find(kw, s)
                if i < 0: break
                abs_off = USERDATA_OFF + off - len(prev) + i
                found.setdefault(kw.decode('latin1'), []).append(abs_off)
                s = i + 1
        prev = buf[-overlap:]
        off += len(data)
for kw, locs in sorted(found.items(), key=lambda x:-len(x[1])):
    print(f"{kw}: {len(locs)} hits, first: {locs[:6]}")
