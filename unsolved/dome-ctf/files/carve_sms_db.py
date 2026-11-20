import struct

f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
MAGIC = b"SQLite format 3\x00"
CHUNK = 16*1024*1024
overlap = len(MAGIC)

offs = []
with open(f, "rb") as fh:
    off = 0
    prev = b""
    while True:
        data = fh.read(CHUNK)
        if not data:
            break
        buf = prev + data
        start = 0
        while True:
            i = buf.find(MAGIC, start)
            if i < 0:
                break
            abs_off = off - len(prev) + i
            offs.append(abs_off)
            start = i + 1
        prev = buf[-overlap:]
        off += len(data)

print("found", len(offs), "SQLite headers at:", offs)

with open(f, "rb") as fh:
    for o in offs:
        fh.seek(o)
        hdr = fh.read(100)
        page_size = struct.unpack(">H", hdr[16:18])[0]
        if page_size == 1:
            page_size = 65536
        page_count = struct.unpack(">I", hdr[28:32])[0]
        size = page_size * page_count
        print(f"offset={o} page_size={page_size} page_count={page_count} total_size={size}")
