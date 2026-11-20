from pwn import *
from capstone import *
libc=ELF('libc.so.6')
md=Cs(CS_ARCH_X86,CS_MODE_64)
# print all symbols containing 'start'
for n,a in libc.symbols.items():
    if 'start' in n.lower():
        print("sym",n,hex(a))
# disassemble __libc_start_call_main if present
for cand in ['__libc_start_call_main']:
    if cand in libc.symbols:
        a=libc.symbols[cand]
        print("=== disasm",cand,hex(a))
        code=libc.read(a,200)
        for i in md.disasm(code,a):
            print(hex(i.address),i.mnemonic,i.op_str)
            if i.mnemonic=='call':
                print("  --> return offset",hex(i.address+i.size))
