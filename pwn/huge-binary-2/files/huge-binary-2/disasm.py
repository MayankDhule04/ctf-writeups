from pwn import *
from capstone import *
context.arch='amd64'
e=ELF('chal',checksec=False)
md=Cs(CS_ARCH_X86,CS_MODE_64)
print("=== all funcs ===")
syms=[(n,a) for n,a in e.symbols.items() if a and a<0x8000]
for n,a in sorted(set(syms),key=lambda x:x[1]):
    print(hex(a),n)
main=e.symbols.get('main')
print("main",hex(main))
# disasm main
code=e.read(main,400)
for ins in md.disasm(code,main):
    print(f"0x{ins.address:x}: {ins.mnemonic} {ins.op_str}")
    if ins.mnemonic=='ret': break
