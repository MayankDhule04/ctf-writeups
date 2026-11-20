import struct
f=r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b=open(f,"rb").read()

# decrypt 349 bytes (LCG) from source rip+0xdf2 @0x12c7 -> rip=0x12ce => 0x12ce+0xdf2=0x20c0
ro_off=0x2000  # file off == vaddr for rodata here (off 0x2000 addr 0x2000)
src_off = ro_off + (0x20c0-0x2000)
N=0xe5+0x78  # 349
eax=0xc0ffee42
dec=bytearray()
for i in range(N):
    eax=(eax*0x41c64e6d+0x3039)&0xffffffff
    ecx=(eax>>16)&0xffffffff
    cl=(ecx ^ b[src_off+i])&0xff
    dec.append(cl)
print("decrypted len", len(dec))

# Now emulate the copy sequence. Each movaps writes 16 bytes from stack[src] to bss[dest].
# stack buffer = dec, indexed by (stack_off - (-0x78)) since rdx started at rsp-0x78 == dec[0].
# src offsets used (relative to rsp): -0x78,-0x68,-0x58,-0x48,-0x38,-0x28,-0x18,-0x08,
#   +0x08,+0x18,+0x28,+0x38,+0x48,+0x58,+0x68,+0x78,+0x88,+0x98,+0xa8,+0xb8,+0xc8, and movdqu +0xd5
# dest rip offsets: 0x2d90,0x2d93,...(+3 each for first 16), then 0x2c5d repeated x5, then 0x2c5a
# Let's compute dest addresses precisely from the instructions.
instr = [
 # (ins_addr, disp, src_stack_off, is16)
 (0x1329,0x2d90,-0x78,16),
 (0x1336,0x2d93,-0x68,16),
 (0x1343,0x2d96,-0x58,16),
 (0x1350,0x2d99,-0x48,16),
 (0x135d,0x2d9c,-0x38,16),
 (0x136a,0x2d9f,-0x28,16),
 (0x1377,0x2da2,-0x18,16),
 (0x1384,0x2da5,-0x08,16),
 (0x1391,0x2da8, 0x08,16),
 (0x139e,0x2dab, 0x18,16),
 (0x13ab,0x2dae, 0x28,16),
 (0x13b8,0x2db1, 0x38,16),
 (0x13c5,0x2db4, 0x48,16),
 (0x13d2,0x2db7, 0x58,16),
 (0x13df,0x2dba, 0x68,16),
 (0x13ec,0x2dbd, 0x78,16),
 (0x13fc,0x2c5d, 0x88,16),
 (0x140c,0x2c5d, 0x98,16),
 (0x141c,0x2c5d, 0xa8,16),
 (0x142c,0x2c5d, 0xb8,16),
 (0x143c,0x2c5d, 0xc8,16),
 (0x144c,0x2c5a, 0xd5,16),  # movups, from movdqu [rsp+0xd5]
]
# dest vaddr = ins_addr + ins_len + disp ; ins for movaps [rip+disp],xmm0 is 7 bytes (0f 29 05 disp32)
# verify: 0x1329 + 7 + 0x2d90 = 0x40c0. good.
mem={}
def stack_index(off):  # off relative to rsp; dec[0] corresponds to rsp-0x78
    return off - (-0x78)
for (ia,disp,soff,ln) in instr:
    dest = ia + 7 + disp
    si = stack_index(soff)
    for k in range(ln):
        mem[dest+k]=dec[si+k]
# Build contiguous bss image
lo=min(mem); hi=max(mem)
print("bss span", hex(lo), hex(hi), "size", hi-lo+1)
img=bytearray(hi-lo+1)
for a,v in mem.items(): img[a-lo]=v
# sbox at 0x40c0, program base rsi=0x4060. But writes start at 0x40c0. Where's 0x4060?
print("first write addr", hex(lo))
# The program (rsi=0x4060) is BELOW 0x40c0 by 0x60. Maybe program is a different buffer written elsewhere,
# OR rsi base differs. Let's just dump what we have around sbox and see if 0x40c0.. is the AES sbox.
sbox_region=img[0x40c0-lo:0x40c0-lo+256] if 0x40c0>=lo else b''
print("at 0x40c0 first16:", " ".join(f"{c:02x}" for c in img[0x40c0-lo:0x40c0-lo+16]))
open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\bss_img.bin","wb").write(img)
print("saved bss_img.bin, base", hex(lo))
