from pwn import *
libc=ELF('libc.so.6')
print("system", hex(libc.symbols['system']))
print("binsh", hex(next(libc.search(b'/bin/sh'))))
print("libc __libc_start_main", hex(libc.symbols['__libc_start_main']))
# find __libc_start_call_main return offset: locate call to main
from capstone import *
md=Cs(CS_ARCH_X86,CS_MODE_64)
for sym in ['__libc_start_call_main','__libc_start_main']:
    if sym in libc.symbols:
        addr=libc.symbols[sym]
        code=libc.read(addr,300)
        print("===",sym,hex(addr))
        for i in md.disasm(code,addr):
            if i.mnemonic=='call' and ('rax' in i.op_str or 'rdx' in i.op_str or 'r12' in i.op_str or 'rbp' in i.op_str):
                print("  call at",hex(i.address),i.op_str,"-> ret",hex(i.address+i.size),"off",hex(i.address+i.size))
