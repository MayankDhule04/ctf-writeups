from pwn import ELF
e = ELF('chal')
# dump rodata strings
for secname in ['.rodata']:
    s = e.get_section_by_name(secname)
    if not s: continue
    data = s.data(); base = s.header['sh_addr']
    cur=b''; start=base
    for i,b in enumerate(data):
        if 32<=b<127:
            if not cur: start=base+i
            cur+=bytes([b])
        else:
            if len(cur)>=3: print(hex(start), cur.decode())
            cur=b''
    if len(cur)>=3: print(hex(start), cur.decode())
