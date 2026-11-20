from pwn import *
context.arch='amd64'
e=ELF('chal',checksec=False)
rop=ROP(e)
for g in ['pop rdi','pop rsi','pop rdx','pop rax','leave','ret','syscall']:
    try:
        addr=rop.find_gadget(g.split())
        print(g,'->',hex(addr.address) if addr else None)
    except Exception as ex:
        print(g,'ERR',ex)
# raw search
import re
text=e.get_section_by_name('.text').data()
base=e.get_section_by_name('.text').header.sh_addr
def find(byts):
    out=[]
    i=text.find(byts)
    while i!=-1:
        out.append(base+i); i=text.find(byts,i+1)
    return [hex(x) for x in out]
print("pop rdi;ret 5f c3 :",find(b'\x5f\xc3'))
print("pop rsi;ret 5e c3 :",find(b'\x5e\xc3'))
print("pop rdx;ret 5a c3 :",find(b'\x5a\xc3'))
print("pop rdi;pop rsi..? 5f 5e c3:",find(b'\x5f\x5e\xc3'))
print("system plt",hex(e.plt['system']))
print("read plt",hex(e.plt['read']))
print("fgets plt",hex(e.plt['fgets']))
print("bss __bss_start",hex(e.symbols.get('__bss_start',0)))
print("total",hex(e.symbols.get('total',0)))
