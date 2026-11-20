import struct, re, sys

f = r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\Custom VM\hyperstate\hyperstate4"
b = open(f, "rb").read()
print("size", len(b))
ei_class = b[4]; ei_data = b[5]
print("class", "64" if ei_class==2 else "32", "endian", "LE" if ei_data==1 else "BE")
is64 = ei_class == 2
en = "<" if ei_data==1 else ">"

if is64:
    e_type,e_machine,e_version,e_entry,e_phoff,e_shoff,e_flags,e_ehsize,e_phentsize,e_phnum,e_shentsize,e_shnum,e_shstrndx = struct.unpack(en+"HHIQQQIHHHHHH", b[16:64])
else:
    e_type,e_machine,e_version,e_entry,e_phoff,e_shoff,e_flags,e_ehsize,e_phentsize,e_phnum,e_shentsize,e_shnum,e_shstrndx = struct.unpack(en+"HHIIIIIHHHHHH", b[16:52])
print("machine", e_machine, "entry", hex(e_entry), "shoff", e_shoff, "shnum", e_shnum, "shstrndx", e_shstrndx)

# section headers
secs=[]
for i in range(e_shnum):
    off = e_shoff + i*e_shentsize
    if is64:
        name,typ,flags,addr,offset,size,link,info,align,entsz = struct.unpack(en+"IIQQQQIIQQ", b[off:off+64])
    else:
        name,typ,flags,addr,offset,size,link,info,align,entsz = struct.unpack(en+"IIIIIIIIII", b[off:off+40])
    secs.append((name,typ,addr,offset,size))
# shstrtab
sname,styp,saddr,soff,ssize = secs[e_shstrndx]
strt = b[soff:soff+ssize]
def nm(o):
    e = strt.find(b"\x00", o); return strt[o:e].decode('latin1')
print("\n== sections ==")
for name,typ,addr,offset,size in secs:
    print(f"{nm(name):20s} type={typ} addr={hex(addr)} off={offset} size={size}")

print("\n== printable strings (len>=4) ==")
for m in re.finditer(rb"[\x20-\x7e]{4,}", b):
    print(m.start(), m.group().decode('latin1'))
