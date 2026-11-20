import os
c0 = bytes.fromhex("43395452000404060301030200040301000205010003020a020300010b030200010f030102004792")
c1 = bytes.fromhex("43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9")

def crc(data):
    v=0xffff
    for byte in data:
        v ^= (byte<<8); v&=0xffff
        for _ in range(8):
            v = ((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v&0xffff

outdir=r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\variants"
os.makedirs(outdir,exist_ok=True)
def save(n,d): open(os.path.join(outdir,n),"wb").write(d); 

for lane,c in [("0",c0),("1",c1)]:
    payload = c[4:-2]           # everything between magic and crc
    rec = b"R9CF" + payload
    rec = rec + crc(rec).to_bytes(2,"big")
    save(f"fix_{lane}.cal", rec)
    print(f"lane{lane} fix: {rec.hex()}  crcok={crc(rec[:-2])==int.from_bytes(rec[-2:],'big')}")
# Also a combined file with both records concatenated (main scans whole buffer for multiple R9CF)
both = open(os.path.join(outdir,"fix_0.cal"),"rb").read()+open(os.path.join(outdir,"fix_1.cal"),"rb").read()
save("fix_both.cal", both)
print("both len", len(both))
