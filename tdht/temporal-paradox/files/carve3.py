b=open(r"Temporal Paradox/gateway_snapshot.img","rb").read()

def hd(off,n=256,label=""):
    print(f"--- {label} @ {hex(off)} ({n} bytes) ---")
    for i in range(0,n,16):
        chunk=b[off+i:off+i+16]
        hexs=' '.join(f'{x:02x}' for x in chunk)
        asc=''.join(chr(x) if 32<=x<127 else '.' for x in chunk)
        print(f"{off+i:08x}  {hexs:<48} {asc}")

# The small-file data region 0xa16000..0xa22000. Filenames were at ...020 offsets (dir entries).
# lane_0.cal / lane_1.cal contents and encoder_crash.fragment content are file data blocks.
# Show blocks around each filename dir-entry inode data — but ext4 data blocks are elsewhere.
# Instead scan 0xa10000..0xa22000 for C9TR (cal) and non-text binary fragments.
import re
for m in re.finditer(rb'C9TR', b):
    print("C9TR at", hex(m.start()))
# Show the region just before the DB (0xa1c000 area = encoder_crash.fragment dir entry)
hd(0xa1c000, 512, "near encoder_crash.fragment dirent")
