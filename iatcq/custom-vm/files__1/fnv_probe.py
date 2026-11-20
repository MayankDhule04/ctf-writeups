def fnv1a(data):
    h=0x811c9dc5
    for b in data:
        h=((h^b)*0x01000193)&0xffffffff
    return h
def fnv1(data):
    h=0x811c9dc5
    for b in data:
        h=((h*0x01000193)&0xffffffff)^b
    return h

TARGET=0x86d03165
cands=[
  "IATCQ{Custom_VM_Reversed}", "IATCQ{custom_vm}", "IATCQ{v1rtu4l_m4ch1n3}",
  "IATCQ{hyperstate}", "IATCQ{HyperState}", "IATCQ{VM_crackme}",
  "Custom VM", "hyperstate", "hyperstate4", "flag", "IATCQ",
]
for c in cands:
    print(f"{c!r:40} fnv1a={fnv1a(c.encode()):08x} fnv1={fnv1(c.encode()):08x}")
print("TARGET", hex(TARGET))
