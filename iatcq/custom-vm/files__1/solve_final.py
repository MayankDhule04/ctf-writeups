from z3 import *
import time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
INSTR = prog_full[0x100:]

SBarr = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256):
    SBarr = Store(SBarr, BitVecVal(i,8), BitVecVal(SBOX[i],8))
def SB(x): return Select(SBarr, x)
def rol3(v): return RotateLeft(v,3)

def build(constrain_printable=True, fixed=None):
    s = Solver()
    inp = [BitVec(f"in_{i}",8) for i in range(32)]
    if fixed:
        for i,ch in enumerate(fixed):
            if ch is not None: s.add(inp[i]==ch)
    if constrain_printable:
        for i in range(32):
            s.add(inp[i]>=0x20, inp[i]<=0x7e)

    def load(idx):  # concrete idx int
        return inp[idx] if idx <= 31 else BitVecVal(0,8)

    # Emulate symbolically. Control flow is input-INDEPENDENT:
    # state[1] starts 0, each round += 2 (d4 01 02), loop until state[1]==0x20 => 16 rounds,
    # processing index pairs (0,1),(2,3),...,(30,31).
    fnv = BitVecVal(0x811c9dc5,32)
    key = BitVecVal(0x42,8)   # state[3] initial (b2 03 42)
    i = 0
    for rnd in range(16):
        # 06 a1 00 01: state0 = input[state1]=input[i]
        s0 = load(i)
        # 09 a7 04 01 ; 0c d4 04 01: state4 = i ; state4 += 1  => i+1
        idx2 = (i+1) & 0xff
        # 0f a1 02 04: state2 = input[state4] = input[i+1]
        s2 = load(idx2)
        # 12 a7 05 03 ; 15 e5 05 00: state5 = rol3(key)
        s5 = rol3(key)
        # 18 a7 04 02: state4=state2 ; 1b c3 04 05: state4 ^= state5
        s4 = s2 ^ s5
        # 1e b6 04 00: state4 = SB(state4)
        s4 = SB(s4)
        # 21 c3 04 00: state4 ^= state0
        s4 = s4 ^ s0
        # 24 a7 00 02: state0 = state2 ; 27 a7 02 04: state2 = state4
        s0 = s2; s2 = s4
        # 2a a7 05 03 ; 2d c3 05 01: state5 = key ^ state1(=i)
        s5 = key ^ BitVecVal(i & 0xff,8)
        # 30 a7 04 02: state4=state2 ; 33 c3 04 05: state4 ^= state5
        s4 = s2 ^ s5
        # 36 b6 04 00: SB
        s4 = SB(s4)
        # 39 c3 04 00: state4 ^= state0
        s4 = s4 ^ s0
        # 3c a7 00 02: state0=state2 ; 3f a7 02 04: state2=state4
        s0 = s2; s2 = s4
        # 42 f6 00 02: FNV mix with state0,state2,state1(=i)
        e = ZeroExt(24,s0) ^ fnv
        e = e * BitVecVal(0x01000193,32)
        cc = (ZeroExt(24,s2) << 8) | ZeroExt(24, BitVecVal(i & 0xff,8))
        e = e ^ cc
        e = e * BitVecVal(0x01000193,32)
        fnv = e
        # 45 c3 00 02: state0 ^= state2 ; 48 a7 03 00: key = state0
        key = s0 ^ s2
        # 4b d4 01 02: state1 += 2
        i += 2
    s.add(fnv == 0x86d03165)
    return s, inp

# First validate structure against emulator on a concrete input by checking model consistency later.
import importlib.util
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

# sanity: my symbolic model's fnv for a FIXED input must equal emulator fnv
def sym_fnv_concrete(inp_bytes):
    fnv=0x811c9dc5; key=0x42; i=0
    def rr(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
    for rnd in range(16):
        s0=inp_bytes[i]
        s2=inp_bytes[i+1] if i+1<=31 else 0
        s5=rr(key)
        s4=s2^s5; s4=SBOX[s4]; s4^=s0
        s0=s2; s2=s4
        s5=key^(i&0xff)
        s4=s2^s5; s4=SBOX[s4]; s4^=s0
        s0=s2; s2=s4
        e=(s0^fnv)&0xffffffff; e=(e*0x01000193)&0xffffffff
        cc=((s2<<8)&0xffffffff)|(i&0xff); e^=cc; e=(e*0x01000193)&0xffffffff
        fnv=e
        key=(s0^s2)&0xff
        i+=2
    return fnv

test=b"A"*32
_, e_st, e_fnv = emu.run2(test)
print("emulator fnv:", hex(e_fnv), "my model fnv:", hex(sym_fnv_concrete(test)), "match:", e_fnv==sym_fnv_concrete(test))

if e_fnv == sym_fnv_concrete(test):
    print("MODEL VALIDATED. Solving with flag format + printable...")
    fixed=[None]*32
    for i,ch in enumerate(b"IATCQ{"): fixed[i]=ch
    fixed[31]=ord('}')
    s, inp = build(constrain_printable=True, fixed=fixed)
    t=time.time(); r=s.check(); print(r, f"{time.time()-t:.1f}s")
    if r==sat:
        m=s.model(); out=bytes(m[inp[i]].as_long() for i in range(32))
        # verify with emulator
        ok,_,fv = emu.run2(out)
        print("candidate:", out.decode('latin1'), "emulator ok:", ok, hex(fv))
    elif r==unsat:
        print("UNSAT with printable+format -> assumptions wrong")
