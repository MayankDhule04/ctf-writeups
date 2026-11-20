from pwn import *
from capstone import *
context.arch='amd64'
e=ELF('chal',checksec=False)
md=Cs(CS_ARCH_X86,CS_MODE_64)

# Scan entire text for endbr64 (function entries)
for sec in e.sections:
    if sec.name == '.text':
        base = sec.header.sh_addr
        data = sec.data()
        print(f"Text: {hex(base)} .. {hex(base+len(data))}")
        for i in range(len(data)-4):
            if data[i:i+4] == b'\xf3\x0f\x1e\xfa':
                addr = base+i
                insns=list(md.disasm(data[i:i+30],addr))[:5]
                syms=[n for n,a in e.symbols.items() if a==addr]
                print(f"  {hex(addr)} {syms}")
                for ins in insns:
                    print(f"    {hex(ins.address)}: {ins.mnemonic} {ins.op_str}")
