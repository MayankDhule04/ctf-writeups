import os
def crc(data):
    v=0xffff
    for byte in data:
        v ^= (byte<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v&0xffff

outdir=r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\variants2"
os.makedirs(outdir,exist_ok=True)
def save(n,d): open(os.path.join(outdir,n),"wb").write(d)

# Record layout per main disasm:
#  [0:4]  "R9CF"
#  [4]    ? (lane?) 
#  [5]    len low
#  [6]    len high   (len = [6]<<8 | [5], TOTAL record length, must be >9 and <= remaining)
#  [7]    ?
#  [8]    module0 id (edi to switch 0x16b1)
#  [9]    module0 param (edx -> r14 = param+0xa boundary)
#  [0xa:] module bytes; iterated: at off, edi=[off], param=[off+1], next boundary rsi+= ...
#  trailer [len-2:len] = crc16(record[0:len-2]) big-endian
# The .cal payload (after its C9TR magic+lane) is the module program. Let's map .cal to this.
# .cal lane0 bytes5.. : 04 04 06 | 03 01 03 02 00 | 04 03 01 00 02 | 05 01 00 03 02 | 0a 02 03 00 01 | 0b 03 02 00 01 | 0f 03 01 02 00
# Interpretation: [count=04?][?04][?06] then records of [tag][4 bytes]. 
# In R9CF terms the loop reads module id at +8, param at +9, then module body of (param) then advances.
# Let's just try: take .cal, replace magic C9TR->R9CF, and set len field [5],[6] to total length (0x28,0x00).
c0 = bytes.fromhex("43395452000404060301030200040301000205010003020a020300010b030200010f030102004792")
c1 = bytes.fromhex("43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9")
for lane,c in [("0",c0),("1",c1)]:
    body = bytearray(c)
    body[0:4]=b"R9CF"
    n=len(body)
    body[5]=n & 0xff
    body[6]=(n>>8)&0xff
    rec=bytes(body[:-2])+crc(bytes(body[:-2])).to_bytes(2,"big")
    save(f"len_{lane}.cal", rec)
    print(f"lane{lane} len-fixed: {rec.hex()}")

# Alternative: maybe .cal offset4 is lane, offset5 = len already but stored differently.
# Try len as big-endian at [5],[6] meaning value 0x0428? too big. 
# Try: the three header bytes after magic+lane in .cal (04 04 06) => maybe [len=0x04? no].
# Build a hand record with a single known module to learn semantics:
# minimal: R9CF, [4]=0, len=0x0e (14), [7]=0, [8]=module id (o4=1), [9]=param 2, then 2 body bytes, crc
for mid in [1]:
    rec=bytearray(b"R9CF"+bytes([0,0,0,0, mid, 2, 0,0]))
    rec[5]=len(rec)+2  # total incl crc, low
    rec[6]=0
    full=bytes(rec)+crc(bytes(rec)).to_bytes(2,"big")
    save(f"hand_mid{mid}.cal", full)
    print("hand:", full.hex(), "len", len(full))
