import struct, zipfile, io

f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"

lfh_offsets = [532688896, 532725760, 532750336, 532758528, 532758853, 532762624, 532762953, 533016576, 533016901, 533020672, 533020997, 533024768, 533025092, 533028864, 533029190, 533032960, 533033286, 533037056, 533037383, 533041152]
eocd_offsets = [532721098, 532725888, 532750551, 532759021, 532763121, 533017069, 533021165, 533025260, 533029358, 533033454, 533037551, 533041640, 533045742]

with open(f, "rb") as fh:
    for idx, eocd_off in enumerate(eocd_offsets):
        fh.seek(eocd_off)
        eocd = fh.read(22)
        comment_len = struct.unpack("<H", eocd[20:22])[0]
        cd_size = struct.unpack("<I", eocd[12:16])[0]
        cd_offset_rel = struct.unpack("<I", eocd[16:20])[0]  # relative offset within the zip
        # find matching start: the nearest LFH offset <= (eocd_off - cd_size - cd_offset_rel) roughly
        # simpler: find greatest LFH offset less than this eocd_off
        candidates = [o for o in lfh_offsets if o < eocd_off]
        start = max(candidates) if candidates else None
        # actual start should be eocd_off - cd_size - cd_offset_rel approx, but let's just try from smallest LFH after previous EOCD
        end = eocd_off + 22 + comment_len
        print(f"--- zip #{idx} EOCD at {eocd_off}, end={end} ---")

with open(f, "rb") as fh:
    # Better: pair each EOCD with the LFH offsets that fall before it and after the previous EOCD
    prev_end = 0
    for idx, eocd_off in enumerate(eocd_offsets):
        fh.seek(eocd_off)
        eocd = fh.read(22)
        comment_len = struct.unpack("<H", eocd[20:22])[0]
        end = eocd_off + 22 + comment_len
        starts_in_range = [o for o in lfh_offsets if prev_end <= o < eocd_off]
        start = min(starts_in_range) if starts_in_range else prev_end
        size = end - start
        fh.seek(start)
        blob = fh.read(size)
        print(f"zip#{idx}: start={start} end={end} size={size}")
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
            for info in zf.infolist():
                enc = bool(info.flag_bits & 0x1)
                print(f"   {info.filename!r} size={info.file_size} encrypted={enc}")
        except Exception as e:
            print("   ERROR opening zip:", e)
        prev_end = end
