import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b = open(f, "rb").read()

# .text: addr 0x10c0 off 4288 size 1461 ; .rodata addr 0x2000 off 8192 size 635
text_addr, text_off, text_size = 0x10c0, 4288, 1461
ro_addr, ro_off, ro_size = 0x2000, 8192, 635

md = Cs(CS_ARCH_X86, CS_MODE_64)
md.detail = True
code = b[text_off:text_off+text_size]
for ins in md.disasm(code, text_addr):
    print(f"0x{ins.address:04x}:\t{ins.mnemonic}\t{ins.op_str}")

print("\n== .rodata hex ==")
ro = b[ro_off:ro_off+ro_size]
for i in range(0, len(ro), 16):
    chunk = ro[i:i+16]
    hexs = " ".join(f"{c:02x}" for c in chunk)
    asc = "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)
    print(f"{ro_addr+i:04x}  {hexs:<48}  {asc}")
