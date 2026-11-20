import struct
f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b = open(f, "rb").read()
# jump table base: lea rdi,[rip+0xb8a] at 0x148f -> rip after instr = 0x1496; 0x1496+0xb8a=0x2020
# table at vaddr 0x2020, file off = 8192 + (0x2020-0x2000) = 8224
base_vaddr = 0x2020
off = 8192 + (base_vaddr - 0x2000)
# index = al + 0x5f, entries are int32 rel to rdi(=0x2020). Range of al: 0xa1..0xc3 -> idx 0x00..0x22
print("idx  al   target")
for idx in range(0x23):
    val = struct.unpack("<i", b[off+idx*4:off+idx*4+4])[0]
    target = (base_vaddr + val) & 0xffffffffffffffff
    al = idx - 0x5f
    print(f"{idx:02x}  0x{(idx-0x5f)&0xff:02x}  0x{target:04x}")
