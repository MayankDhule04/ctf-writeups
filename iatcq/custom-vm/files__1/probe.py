import importlib.util, os, random
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec)
# emulate.py runs a trace at import under __main__ guard; safe.
spec.loader.exec_module(emu)

def check(inp):
    ok, st, fnv = emu.run2(inp)
    return ok, st[1], fnv

for trial in range(8):
    inp = bytes([random.randint(0x20,0x7e) for _ in range(32)])
    ok, s1, fnv = check(inp)
    print(f"s1={s1:#x} fnv={fnv:08x} ok={ok}  inp={inp[:12]!r}")

# Does state[1] always end at 0x20? Instrument state[2] increments.
INSTR = emu.INSTR; SBOX = emu.SBOX
def rol8(v,n): v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff
def run_incr(inp):
    st=[0]*16; fnv=0x811c9dc5; eq=0; pc=0; incrs=[]
    g=0
    while pc<=0x5c:
        op=INSTR[pc]; a1=INSTR[pc+1]; a2=INSTR[pc+2]
        if op==0xB2: st[a1]=a2&0xff; pc+=3
        elif op==0xA7: st[a1]=st[a2]; pc+=3
        elif op==0xA1:
            idx=st[a2]; st[a1]=inp[idx] if idx<=0x1f else 0; pc+=3
        elif op==0xE5: st[a1]=rol8(st[a1],3); pc+=3
        elif op==0xC3:
            c=st[a1]; a=st[a2]; eq=1 if (c&0xff)==(a&0xff) else 0; st[a1]=(c^a)&0xff; pc+=3
        elif op==0xB6: st[a1]=SBOX[st[a1]]; pc+=3
        elif op==0xD4:
            if pc==0x4b: incrs.append(st[a2])
            st[a1]=(st[a1]+a2)&0xff; pc+=3
        elif op==0x17:
            pc+=3
            if eq==0: pc=a1
        elif op==0xF6:
            e=st[a1]^fnv; e&=0xffffffff; e=(e*0x01000193)&0xffffffff
            cc=(st[a2]<<8)&0xffffffff; cc|=st[1]; e^=cc; e=(e*0x01000193)&0xffffffff; fnv=e; pc+=3
        elif op==0xE9: pc+=3; return incrs, st[1], fnv
        elif op==0xFF: break
        g+=1
        if g>5000: break
    return incrs, st[1], fnv

incrs, s1, fnv = run_incr(b"A"*32)
print("increments for A*32:", incrs, "final s1", hex(s1))
incrs, s1, fnv = run_incr(b"IATCQ{AAAAAAAAAAAAAAAAAAAAAAAA}")
print("increments for flagish:", incrs, "final s1", hex(s1))
