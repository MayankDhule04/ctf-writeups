from z3 import *

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
INSTR = prog_full[0x100:]

def sbox_expr(x):
    # x is BitVec 8; build a nested If chain via Select over an Array
    arr = Array('sbox', BitVecSort(8), BitVecSort(8))
    return arr, x

s = Solver()
inp = [BitVec(f"in_{i}", 8) for i in range(32)]

# printable ascii constraint + flag format IATCQ{...}
prefix = b"IATCQ{"
for i,ch in enumerate(prefix):
    s.add(inp[i] == ch)
s.add(inp[31] == ord('}'))
for i in range(len(prefix), 31):
    s.add(inp[i] >= 0x20, inp[i] <= 0x7e)

# Build a symbolic sbox as an Array constant
SB = Array('SB', BitVecSort(8), BitVecSort(8))
for i in range(256):
    SB = Store(SB, i, BitVecVal(SBOX[i], 8))

def rol3(v):
    return RotateLeft(v, 3)

# state as python list of BitVec exprs (8-bit)
state = [BitVecVal(0,8) for _ in range(16)]
fnv = BitVecVal(0x811c9dc5, 32)
pc = 0
# We must run concretely on control flow (pc), since only the final compare depends on input.
# state[1] (the loop counter) evolves deterministically regardless of input, so pc trace is fixed.
# Emulate symbolically following the SAME concrete control path as the "A"*32 run.
steps = 0
# Track concrete loop counter to drive the conditional 0x17 exactly like hardware.
# state[1] is symbolic-free (depends only on constants), so we can evaluate it concretely.
# We'll keep a parallel concrete copy for the counter-relevant bytes? Simpler: the eq-flag for 0x17
# comes from a c3 on state[5] vs state[1] where state[5]=0x20; loop continues until state[1]==0x20.
# We reproduce control by concretely simulating the counter.

# concrete simulation of control (counter) using same ops but ignoring input value for pc decisions
def concrete_counter_path():
    st=[0]*16; eq=0; pc=0; path=[]
    def rol8(v,n): v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff
    while pc<=0x5c:
        op=INSTR[pc]; a1=INSTR[pc+1]; a2=INSTR[pc+2]; path.append(pc)
        if op==0xB2: st[a1]=a2&0xff; pc+=3
        elif op==0xA7: st[a1]=st[a2]; pc+=3
        elif op==0xA1:
            idx=st[a2]; st[a1]= (0x41 if idx<=0x1f else 0); pc+=3  # dummy input value; counter path independent
        elif op==0xE5: st[a1]=rol8(st[a1],3); pc+=3
        elif op==0xC3:
            c=st[a1]; a=st[a2]; eq=1 if (c&0xff)==(a&0xff) else 0; st[a1]=(c^a)&0xff; pc+=3
        elif op==0xB6: st[a1]=SBOX[st[a1]]; pc+=3
        elif op==0xD4: st[a1]=(st[a1]+a2)&0xff; pc+=3
        elif op==0x17:
            pc+=3
            if eq==0: pc=a1
        elif op==0xF6: pc+=3
        elif op==0xE9: pc+=3; return path
        elif op==0xFF: break
        else: break
    return path

# But the eq-flag for the loop depends on state values that ARE input-dependent in general.
# Check: the c3 right before 0x17 (pc=0x51) is state[5]^state[1] with state[5]=0x20 preloaded (b2 05 20),
# and state[1]=counter. eq = (0x20 == counter). So loop control depends ONLY on the counter. Safe.

# Now symbolic run following fixed structure: iterate 32 times of the body, then final.
# Body pc range: 0x06..0x56 then jumps to 0x06; iteration count until state[1]==0x20.
# We'll just run the interpreter symbolically with a concrete pc, using concrete counter for 0x17.

def sym_run():
    global fnv
    st=[BitVecVal(0,8) for _ in range(16)]
    cnt=[0]*16   # concrete shadow for control + indices
    fnvv=BitVecVal(0x811c9dc5,32)
    eqc=0
    pc=0
    guard=0
    def rol8(v,n): v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff
    while pc<=0x5c:
        op=INSTR[pc]; a1=INSTR[pc+1]; a2=INSTR[pc+2]
        if op==0xB2:
            st[a1]=BitVecVal(a2&0xff,8); cnt[a1]=a2&0xff; pc+=3
        elif op==0xA7:
            st[a1]=st[a2]; cnt[a1]=cnt[a2]; pc+=3
        elif op==0xA1:
            idx=cnt[a2]
            if idx<=0x1f:
                st[a1]=inp[idx]
            else:
                st[a1]=BitVecVal(0,8)
            cnt[a1]=idx  # not really used as value; keep placeholder
            pc+=3
        elif op==0xE5:
            st[a1]=rol3(st[a1]); cnt[a1]=rol8(cnt[a1],3); pc+=3
        elif op==0xC3:
            c=st[a1]; a=st[a2]
            eqc=1 if (cnt[a1]&0xff)==(cnt[a2]&0xff) else 0
            st[a1]=c^a; cnt[a1]=(cnt[a1]^cnt[a2])&0xff; pc+=3
        elif op==0xB6:
            st[a1]=Select(SB, st[a1]); cnt[a1]=SBOX[cnt[a1]]; pc+=3
        elif op==0xD4:
            st[a1]=st[a1]+BitVecVal(a2,8); cnt[a1]=(cnt[a1]+a2)&0xff; pc+=3
        elif op==0x17:
            pc+=3
            if eqc==0: pc=a1
        elif op==0xF6:
            e=ZeroExt(24, st[a1])
            e=e ^ fnvv
            e=e * BitVecVal(0x01000193,32)
            cc=ZeroExt(24, st[a2]) << 8
            cc=cc | ZeroExt(24, st[1])
            e=e ^ cc
            e=e * BitVecVal(0x01000193,32)
            fnvv=e
            pc+=3
        elif op==0xE9:
            pc+=3
            return fnvv, st
        elif op==0xFF: break
        else:
            print("unknown", hex(op)); break
        guard+=1
        if guard>5000: print("runaway"); break
    return fnvv, st

fnv_final, st_final = sym_run()
s.add(fnv_final == 0x86d03165)

print("solving...")
r = s.check()
print(r)
if r == sat:
    m = s.model()
    out = bytes(m[inp[i]].as_long() for i in range(32))
    print("FLAG:", out.decode('latin1'))
