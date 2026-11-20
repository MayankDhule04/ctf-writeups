from pwn import *
e=ELF('chal',checksec=False)
data=e.read(0x2000,0x200)
cur=b''
for idx,b in enumerate(data):
    if b==0:
        if cur:
            print(hex(0x2000+idx-len(cur)), repr(cur))
        cur=b''
    else:
        cur+=bytes([b])
