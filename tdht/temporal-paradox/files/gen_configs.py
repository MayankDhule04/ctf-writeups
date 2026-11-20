import os
def crc(data):
    v=0xffff
    for byte in data:
        v ^= (byte<<8); v&=0xffff
        for _ in range(8):
            v=((v<<1)^0x1021)&0xffff if v&0x8000 else (v<<1)&0xffff
    return v&0xffff

lane0=[1,4,7,9,12,14,16]   # o4,da,c8,cr,x3,ml,lc
lane1=[1,3,6,8,11,14,16]   # o4,dx,c7,cf,g8,ml,lc

outdir=r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\configs"
os.makedirs(outdir,exist_ok=True)
def save(n,d): open(os.path.join(outdir,n),"wb").write(d)

# main parse recap:
#  [8]=module0 id, [9]=module0 param(len of its data), boundary r14=param+0xa
#  then inner loop from off: id=[off], plen=[off+1], advance off += plen+2 ish
# So encoding: header(8 bytes) then sequence of [id][paramlen][param bytes...]
# module0 special: id@8, plen@9, data@0xa..0xa+plen ; next module at 0xa+plen: id,plen,...
# Let's encode each module with paramlen=0 (no body) -> [id][0] pairs after header.

def build(mods, lane, hdr7=(0,0,0), first_hdr=(0,0)):
    # header: R9CF + [4]=lane + [5],[6]=len + [7]=hdrbyte
    body = bytearray(b"R9CF")
    body.append(lane)      # [4]
    body.append(0); body.append(0)  # [5],[6] len placeholder
    body.append(hdr7[0] if hdr7 else 0)  # [7]
    # modules: module0 at [8]=id [9]=plen, then data
    for i,m in enumerate(mods):
        body.append(m)     # id
        body.append(0)     # plen = 0
    # pad + crc
    n=len(body)+2
    body[5]=n & 0xff; body[6]=(n>>8)&0xff
    rec=bytes(body)+crc(bytes(body)).to_bytes(2,"big")
    return rec

for lane,mods,nm in [(0,lane0,"lane0"),(1,lane1,"lane1")]:
    save(f"{nm}_p0.cal", build(mods,lane))

# variant: paramlen=1 with a data byte = slot index
def build2(mods, lane):
    body=bytearray(b"R9CF"); body.append(lane); body+=b"\x00\x00\x00"
    for i,m in enumerate(mods):
        body.append(m); body.append(1); body.append(i)
    n=len(body)+2; body[5]=n&0xff; body[6]=(n>>8)&0xff
    return bytes(body)+crc(bytes(body)).to_bytes(2,"big")
for lane,mods,nm in [(0,lane0,"lane0"),(1,lane1,"lane1")]:
    save(f"{nm}_p1slot.cal", build2(mods,lane))

print("done, files:", os.listdir(outdir))
