from z3 import *
import time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
INSTR = prog_full[0x100:]

# Build a Z3 function for the S-box lookup as a big If-chain is slow; use an Array constant once.
SBarr = K(BitVecSort(8), BitVecVal(0,8))
for i in range(256):
    SBarr = Store(SBarr, BitVecVal(i,8), BitVecVal(SBOX[i],8))
def SB(x): return Select(SBarr, x)

def rol3(v): return RotateLeft(v, 3)

s = Solver()
inp = [BitVec(f"in_{i}",8) for i in range(32)]
prefix = b"IATCQ{"
for i,ch in enumerate(prefix):
    s.add(inp[i]==ch)
s.add(inp[31]==ord('}'))
for i in range(len(prefix),31):
    s.add(inp[i]>=0x20, inp[i]<=0x7e)

def load_input(idx_bv):
    # returns input[idx] if idx<=31 else 0 ; idx is BitVec8
    res = BitVecVal(0,8)
    for k in range(32):
        res = If(idx_bv==k, inp[k], res)
    return res

# Symbolic execution: state[1] evolves by state[2]; we must follow control concretely,
# but state[1],state[2],state[3] are input-dependent. So we cannot precompute the path.
# However, from the "A" trace state[1] advanced by 1 each round (state[2] ended =1).
# The counter add is d4 01 02: state[1]+=state[2]. For the loop to hit exactly 0x20 and
# read indices 0..31 once, the design intends state[2]==1 at pc=4b each round.
# We enforce that as a constraint (state[2]==1 at the counter-add) so the machine walks
# indices 0..31 in order — this is the "walk through correctly" hint. If UNSAT we revisit.

fnv = BitVecVal(0x811c9dc5,32)
state3 = BitVecVal(0x42,8)   # initial key (b2 03 42 sets state[3]=0x42 before loop)
# Note: b2 01 00 sets state[1]=0 ; b2 03 42 sets state[3]=0x42 (pre-loop, pc 00 and 03)

for i in range(32):
    s0 = inp[i]                       # state[0]=input[i]
    s4 = BitVecVal((i+1)&0xff,8)      # state[4]=i+1
    s2 = load_input(s4)               # state[2]=input[i+1] (0 if i+1>31)
    s5 = rol3(state3)                 # state[5]=rol(key,3)
    s4 = s2 ^ s5
    s4 = SB(s4)
    s4 = s4 ^ s0                      # ^ input[i]
    s0b = s2                          # state[0]=input[i+1]
    s2b = s4
    s5 = state3 ^ BitVecVal(i,8)      # state[5]=key ^ i
    s4 = s2b ^ s5
    s4 = SB(s4)
    s4 = s4 ^ s0b                     # ^ input[i+1]
    s0c = s2b
    s2c = s4
    # FNV mix f6 00 02 : uses state[0]=s0c, state[2]=s2c, and state[1]=i
    e = ZeroExt(24, s0c) ^ fnv
    e = e * BitVecVal(0x01000193,32)
    cc = (ZeroExt(24, s2c) << 8) | ZeroExt(24, BitVecVal(i,8))
    e = e ^ cc
    e = e * BitVecVal(0x01000193,32)
    fnv = e
    # c3 00 02: state[0]^=state[2]
    s0d = s0c ^ s2c
    # a7 03 00: state[3]=state[0]  (key feedback)
    state3 = s0d
    # d4 01 02 counter add: enforce walk-by-1 => state[2] (==s2c) must equal 1
    s.add(s2c == 1)

s.add(fnv == 0x86d03165)

print("solving...")
t=time.time()
s.set("timeout", 120000)
r = s.check()
print(r, f"{time.time()-t:.1f}s")
if r==sat:
    m=s.model()
    out=bytes(m[inp[i]].as_long() for i in range(32))
    print("FLAG:", out.decode('latin1'))
