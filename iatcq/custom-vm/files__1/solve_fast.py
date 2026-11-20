from z3 import *
import importlib.util, time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])

spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

SBarr = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256):
    SBarr = Store(SBarr, BitVecVal(i,8), BitVecVal(SBOX[i],8))
def SB(x): return Select(SBarr, x)

def solve(free_positions, fixed_map):
    s = Solver()
    inp = []
    for i in range(32):
        v = BitVec(f"in_{i}",8)
        inp.append(v)
        if i in fixed_map:
            s.add(v == fixed_map[i])
        else:
            s.add(v >= 0x20, v <= 0x7e)
    def load(idx): return inp[idx] if idx <= 31 else BitVecVal(0,8)
    fnv = BitVecVal(0x811c9dc5,32); key = BitVecVal(0x42,8); i=0
    for rnd in range(16):
        s0=load(i); s2=load((i+1)&0xff)
        s5=RotateLeft(key,3)
        s4=SB(s2 ^ s5) ^ s0
        s0=s2; s2=s4
        s5=key ^ BitVecVal(i&0xff,8)
        s4=SB(s2 ^ s5) ^ s0
        s0=s2; s2=s4
        e=(ZeroExt(24,s0) ^ fnv) * BitVecVal(0x01000193,32)
        cc=(ZeroExt(24,s2)<<8) | ZeroExt(24, BitVecVal(i&0xff,8))
        e=(e ^ cc) * BitVecVal(0x01000193,32)
        fnv=e
        key=s0 ^ s2
        i+=2
    s.add(fnv == 0x86d03165)
    if s.check()==sat:
        m=s.model()
        return bytes(m[inp[k]].as_long() for k in range(32))
    return None

# Fix format bytes + fill inner with 'A', leave last 8 inner bytes (pos 22..29) free.
fixed = {}
for i,ch in enumerate(b"IATCQ{"): fixed[i]=ch
fixed[31]=ord('}')
for i in range(6,22): fixed[i]=ord('A')
free = list(range(22,30))
t=time.time()
out = solve(free, fixed)
print(f"{time.time()-t:.1f}s")
if out:
    ok,_,fv = emu.run2(out)
    print("KEY:", out.decode('latin1', 'replace'))
    print("emulator ACCESS GRANTED:", ok, "fnv", hex(fv))
else:
    print("UNSAT for this fixing")
