import struct

f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
start = 532688896
eocd_off = 532721098

with open(f, "rb") as fh:
    fh.seek(eocd_off)
    eocd = fh.read(22)
    comment_len = struct.unpack("<H", eocd[20:22])[0]
    end = eocd_off + 22 + comment_len
    print("EOCD comment len:", comment_len, "zip end:", end, "zip size:", end-start)

    fh.seek(start)
    blob = fh.read(end - start)

outpath = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421_carved.zip"
with open(outpath, "wb") as out:
    out.write(blob)
print("wrote", outpath, len(blob), "bytes")
