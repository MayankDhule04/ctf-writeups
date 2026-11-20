from pwn import ELF
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

e = ELF('chal')
md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = False

funcs = ['main','setup','get_char','peek_char','parse_json_object','do_parse_json_object','run_aligned','print_and_exit']
# build symbol->size map from ELF symtab
sizes = {}
for sym in e.symbols:
    pass

# Use the raw symtab for sizes
from elftools.elf.elffile import ELFFile
f = open('chal','rb')
ef = ELFFile(f)
symtab = ef.get_section_by_name('.symtab')
info = {}
for s in symtab.iter_symbols():
    if s.name in funcs:
        info[s.name] = (s['st_value'], s['st_size'])

for name in funcs:
    if name not in info:
        print(f"== {name}: not found =="); continue
    addr, size = info[name]
    data = e.read(addr, size)
    print(f"\n===== {name} @ {hex(addr)} size {size} =====")
    for i in md.disasm(data, addr):
        print(f"{i.address:#06x}:\t{i.mnemonic}\t{i.op_str}")
