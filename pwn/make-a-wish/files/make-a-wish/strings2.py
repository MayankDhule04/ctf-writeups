from pwn import *
e=ELF('chal')
data=e.read(0x402000,0x300)
off=0x402000
i=0
cur=b''
start=off
for idx,b in enumerate(data):
    if b==0:
        if cur:
            print(hex(off+idx-len(cur)), repr(cur))
        cur=b''
    else:
        cur+=bytes([b])
