from pwn import *
from capstone import *
context.arch='amd64'
e=ELF('chal')
md=Cs(CS_ARCH_X86,CS_MODE_64)
md.detail=False
funcs={'sub_401296':0x401296,'split':0x4012e5,'menu':0x40137e,'create':0x4013b6,'delete':0x4014fd,'main':0x40160f}
order=sorted(funcs.items(),key=lambda x:x[1])
ends={}
addrs=[a for _,a in order]+[0x401874]
for i,(n,a) in enumerate(order):
    ends[n]=addrs[i+1]
for n,a in order:
    print("==============",n,hex(a),"==============")
    code=e.read(a,ends[n]-a)
    for ins in md.disasm(code,a):
        print(f"0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
# rodata strings
print("==== rodata ====")
for a in range(0x402000,0x402200,1):
    pass
