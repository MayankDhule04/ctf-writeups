import os

# module name table from binary (idx -> name), order at .rodata 0x22b7
MODS = ["o3","o4","o5","dx","da","ds","c7","c8","cf","cr","sn","g8","x3","mh","ml","xs","lc","zl","bz","xz"]

# authoritative lane orders from runtime_events (the effective loaded modules)
LANE0 = ["o4","da","c8","cr","x3","ml","lc"]
LANE1 = ["o4","dx","c7","cf","g8","ml","lc"]

def parse(rec):
    # R9CF(4) [4]=? [5,6]=len(le) [7]=? then entries [mod_id][paylen][payload...]
    assert rec[:4]==b"R9CF", rec[:4]
    ln = rec[5] | (rec[6]<<8)
    b4=rec[4]; b7=rec[7]
    i=8
    entries=[]
    while i < ln-2:  # last 2 bytes may be crc/trailer; entries region
        mid=rec[i]; pl=rec[i+1]
        payload=rec[i+2:i+2+pl]
        entries.append((mid, MODS[mid] if mid<len(MODS) else f"?{mid:02x}", pl, payload.hex()))
        i += 2+pl
    return b4,ln,b7,entries,rec[i:].hex()

for i in range(12):
    p=f"r9cf/rec{i:02d}.bin"
    if not os.path.exists(p): continue
    rec=open(p,"rb").read()
    b4,ln,b7,entries,tail=parse(rec)
    names=[e[1] for e in entries]
    print(f"rec{i:02d} b4={b4:02x} len={ln} b7={b7:02x} tail={tail}")
    print("   seq:", names)
    for e in entries:
        print(f"      id={e[0]:2d} {e[1]} len={e[2]} payload={e[3]}")
