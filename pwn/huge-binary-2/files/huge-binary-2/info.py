from pwn import *
context.arch='amd64'
e=ELF('chal')
print("PIE:",e.pie,"RELRO:",e.relro,"NX:",e.nx,"Canary:",e.canary)
print("Entry:",hex(e.entry))
print("=== funcs/syms ===")
for name,addr in sorted(e.symbols.items(),key=lambda x:x[1]):
    if 0x400000<=addr<0x500000:
        print(hex(addr),name)
print("=== plt ===")
for k,v in e.plt.items(): print(hex(v),k)
print("=== got ===")
for k,v in e.got.items(): print(hex(v),k)
