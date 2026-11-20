from pwn import *
e=ELF('chal')
for a in [0x402008,0x402019,0x40201c,0x402040,0x402065,0x402070,0x402096]:
    s=e.read(a,64).split(b'\x00')[0]
    print(hex(a), repr(s))
