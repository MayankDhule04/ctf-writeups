import struct
f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b=open(f,"rb").read()

# Parse ELF sections
e_shoff,=struct.unpack("<Q",b[0x28:0x30])
e_shentsize,e_shnum,e_shstrndx=struct.unpack("<HHH",b[0x3a:0x40])
secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    nm,typ,fl,addr,offset,size,link,info,al,ent=struct.unpack("<IIQQQQIIQQ",b[off:off+64])
    secs.append((nm,typ,addr,offset,size))
so,ss=secs[e_shstrndx][3],secs[e_shstrndx][4]; strt=b[so:so+ss]
def nm(o): e=strt.find(b"\0",o); return strt[o:e].decode('latin1')
print("== all sections ==")
for s in secs:
    print(f"{nm(s[0]):18s} type={s[1]:2d} addr={s[2]:#08x} off={s[3]:#08x} size={s[4]:#06x}")

# The encrypted program: at 0x12c7 lea rsi,[rip+0xdf2] -> 0x20c0. init_vm decrypts N bytes.
# Length: rdi=[rsp+0xe5], rdx=[rsp-0x78] => 0xe5+0x78 = 0x15d = 349. We know sbox(256)+prog(93).
# Let's decrypt a LARGE span from 0x20c0 to end of rodata to see if more structure/flag hides.
ro=[s for s in secs if nm(s[0])==".rodata"][0]
ro_off=ro[3]; ro_addr=ro[2]; ro_size=ro[4]
enc_start_off = ro_off + (0x20c0-ro_addr)
span = b[enc_start_off: ro_off+ro_size]
eax=0xc0ffee42
dec=bytearray()
for i in range(len(span)):
    eax=(eax*0x41c64e6d+0x3039)&0xffffffff
    ecx=(eax>>16)&0xffffffff
    dec.append((ecx^span[i])&0xff)
print(f"\n== decrypted {len(dec)} bytes from 0x20c0 ==")
# show region after the program (offset >= 349) as ascii
tail=dec[349:]
print("post-program ascii:", "".join(chr(c) if 32<=c<127 else '.' for c in tail))
# search for IATCQ in decrypted
import re
for m in re.finditer(rb"[\x20-\x7e]{5,}", bytes(dec)):
    s=m.group().decode('latin1')
    if len(s)>=6:
        print("STR@",m.start(),repr(s))
