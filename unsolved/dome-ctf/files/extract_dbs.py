import struct, os, sqlite3

f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
outdir = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\carved_dbs"
os.makedirs(outdir, exist_ok=True)

headers = [532180992, 532791296, 532803584, 532815872, 532828160, 532836352,
           532852736, 532860928, 532889600, 532901888, 532914176, 532946944,
           532959232, 532975616, 533008384]

with open(f, "rb") as fh:
    for o in headers:
        fh.seek(o)
        hdr = fh.read(100)
        page_size = struct.unpack(">H", hdr[16:18])[0]
        if page_size == 1:
            page_size = 65536
        page_count = struct.unpack(">I", hdr[28:32])[0]
        size = page_size * page_count
        fh.seek(o)
        blob = fh.read(size)
        outpath = os.path.join(outdir, f"db_{o}.sqlite")
        with open(outpath, "wb") as out:
            out.write(blob)
        # try to open and list tables
        try:
            con = sqlite3.connect(outpath)
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            print(f"{o}: tables={tables}")
            con.close()
        except Exception as e:
            print(f"{o}: ERROR {e}")
