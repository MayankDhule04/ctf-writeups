import re
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"

leads = [b"IMG_4421", b"darkvault", b"blackvault", b"lockbox", b"vault",
         b".zip", b"dcode", b"cipher", b"vigenere", b"vigen\xc3\xa8re",
         b"github", b"pastebin", b"gist", b"gitlab", b"keybase",
         b"nightfall", b"operation"]

CHUNK = 8*1024*1024
overlap = 512
found = {}
with open(f, "rb") as fh:
    off = 0; prev = b""
    while True:
        data = fh.read(CHUNK)
        if not data: break
        buf = prev + data
        for kw in leads:
            s = 0
            while True:
                i = buf.find(kw, s)
                if i < 0: break
                abs_off = off - len(prev) + i
                found.setdefault(kw.decode('latin1', 'replace'), []).append(abs_off)
                s = i + 1
        prev = buf[-overlap:]
        off += len(data)
for kw, locs in sorted(found.items(), key=lambda x:-len(x[1])):
    print(f"{kw}: {len(locs)} hits, first: {locs[:10]}")
