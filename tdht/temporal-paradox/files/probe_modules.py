import os
def crc(data):
    v=0xffff
    for b in data:
        v^=(b<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v&0xffff

out=r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\probe"
os.makedirs(out,exist_ok=True)

# Wire record layout learned:
#  [0:4]=R9CF  [4]=lane  [5],[6]=len(LE total incl crc)  [7]=hdr
#  [8]=module0 id  [9]=module0 paramlen  then that many param bytes
#  subsequent modules: [id][paramlen][params...]
#  trailer=crc16(rec[0:len-2]) big-endian
def rec(mods, lane=0, hdr=0):
    b=bytearray(b"R9CF"); b.append(lane); b+= b"\x00\x00"; b.append(hdr)
    for (mid,params) in mods:
        b.append(mid); b.append(len(params)); b+=bytes(params)
    n=len(b)+2; b[5]=n&0xff; b[6]=(n>>8)&0xff
    return bytes(b)+crc(bytes(b)).to_bytes(2,"big")

# one file per single module id, paramlen 0
for mid in range(0x14):
    open(os.path.join(out,f"m{mid:02d}.cal"),"wb").write(rec([(mid,[])]))
# also the two real lanes, modules with paramlen 0
lane0=[1,4,7,9,12,14,16]; lane1=[1,3,6,8,11,14,16]
open(os.path.join(out,"LANE0.cal"),"wb").write(rec([(m,[]) for m in lane0],lane=0))
open(os.path.join(out,"LANE1.cal"),"wb").write(rec([(m,[]) for m in lane1],lane=1))
print("wrote", len(os.listdir(out)), "files")
