import struct

f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b = open(f, "rb").read()
ro_off = 8192; ro_addr = 0x2000
def rd(addr, n):
    return b[ro_off + (addr-ro_addr): ro_off + (addr-ro_addr) + n]

# init_vm @0x12c0:
#  rsi = rip+0xdf2 at 0x12ce? Actually lea rsi,[rip+0xdf2] at 0x12c7: rip=0x12ce -> 0x20c0 (encrypted src)
#  eax = 0xc0ffee42 (LCG state)
#  loop 0x1300: for each byte:
#     eax = eax*0x41c64e6d + 0x3039   (LCG)
#     ecx = eax >> 16
#     cl ^= src[i]
#     dst[i] = cl
#  count = rdi-rdx region: rdi=[rsp+0xe5], rdx=[rsp-0x78]; length = 0xe5-(-0x78)=0x15d=349
src_addr = 0x20c0
# number of iterations: rdx from rsp-0x78 to rdi rsp+0xe5 => 0xe5 - (-0x78) = 349
N = 0xe5 + 0x78
src = rd(src_addr, N)
eax = 0xc0ffee42
out = bytearray()
for i in range(N):
    eax = (eax * 0x41c64e6d + 0x3039) & 0xffffffff
    ecx = (eax >> 16) & 0xffffffff
    cl = (ecx ^ src[i]) & 0xff
    out.append(cl)
print("prog len", len(out))
for i in range(0, len(out), 16):
    chunk = out[i:i+16]
    print(f"{i:04x}  " + " ".join(f"{c:02x}" for c in chunk))
open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","wb").write(out)
