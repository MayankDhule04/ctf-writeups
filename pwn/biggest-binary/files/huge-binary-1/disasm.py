from pwn import *
context.arch='amd64'
e=ELF('chal')
from capstone import *
md=Cs(CS_ARCH_X86,CS_MODE_64)
def dis(name,addr,size):
    print("===",name,hex(addr),"===")
    code=e.read(addr,size)
    for i in md.disasm(code,addr):
        print(f"0x{i.address:x}:\t{i.mnemonic}\t{i.op_str}")
dis("main",e.symbols['main'],e.symbols['_fini']-e.symbols['main'])
print("arghhhh addr", hex(e.symbols['arghhhh']))
