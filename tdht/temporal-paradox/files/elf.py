import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

f = r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\extracted\usr\local\sbin\r9sampler"
b = open(f,"rb").read()
en="<"; is64=True
e_shoff, = struct.unpack("<Q", b[0x28:0x30])
e_shentsize, e_shnum, e_shstrndx = struct.unpack("<HHH", b[0x3a:0x40])
secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    name,typ,flags,addr,offset,size,link,info,align,entsz = struct.unpack("<IIQQQQIIQQ", b[off:off+64])
    secs.append([name,typ,addr,offset,size])
shstr_off=secs[e_shstrndx][3]; shstr_size=secs[e_shstrndx][4]
strt=b[shstr_off:shstr_off+shstr_size]
def nm(o):
    e=strt.find(b"\0",o); return strt[o:e].decode('latin1')
S={}
for s in secs:
    S[nm(s[0])]=s
def dump(name):
    if name not in S: print(name,"MISSING"); return
    _,_,addr,off,size=S[name]
    data=b[off:off+size]
    print(f"== {name} addr={addr:#x} size={size} ==")
    for i in range(0,len(data),16):
        ch=data[i:i+16]
        print(f"{addr+i:#06x}  "+" ".join(f"{c:02x}" for c in ch)+"   "+"".join(chr(c) if 32<=c<127 else '.' for c in ch))

for n in [".rodata",".data.rel.ro",".data"]:
    dump(n); print()

# disasm .text
_,_,taddr,toff,tsize=S[".text"]
md=Cs(CS_ARCH_X86,CS_MODE_64); md.detail=False
code=b[toff:toff+tsize]
out=[]
for ins in md.disasm(code,taddr):
    out.append(f"{ins.address:#06x}:\t{ins.mnemonic}\t{ins.op_str}")
open(r"c:\Users\mayan\OneDrive\Desktop\ctf\Temporal_Paradox\text_disasm.txt","w").write("\n".join(out))
print("disasm lines:",len(out))
