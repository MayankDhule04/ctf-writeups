from pwn import *
context.arch = 'amd64'
e = ELF('chal')
print("Arch:", e.arch, "bits:", e.bits)
print("PIE:", e.pie, "RELRO:", e.relro, "NX:", e.nx, "Canary:", e.canary)
print("Entry:", hex(e.entry))
print("=== Symbols (functions) ===")
for name, addr in sorted(e.symbols.items(), key=lambda x: x[1]):
    if e.pie:
        pass
    print(hex(addr), name)
print("=== GOT ===")
for k,v in e.got.items():
    print(hex(v), k)
print("=== PLT ===")
for k,v in e.plt.items():
    print(hex(v), k)
