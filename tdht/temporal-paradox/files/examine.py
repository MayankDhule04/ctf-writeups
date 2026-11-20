p=r"Temporal Paradox/gateway_snapshot.img"
b=open(p,"rb").read()

def hexdump(off,n,label=""):
    print(f"--- {label} @ {hex(off)} ({n} bytes) ---")
    d=b[off:off+n]
    for i in range(0,len(d),16):
        ch=d[i:i+16]
        print(f"{off+i:08x}  "+" ".join(f"{c:02x}" for c in ch).ljust(48)+" "+"".join(chr(c) if 32<=c<127 else '.' for c in ch))

# egress region
hexdump(0x15df745-32, 256, "egress area")
# R9CF first block
hexdump(0x15cf30a, 96, "R9CF block 0")
# the HTF region (decoys) - show a couple
hexdump(0x15df745-0x200, 0x400, "around egress -0x200")
