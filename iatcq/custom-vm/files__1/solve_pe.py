from z3 import *
import importlib.util, time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

def SB(x):
    if isinstance(x, int):
        return SBOX[x & 0xff]
    # pure QF_BV If-chain (no array theory)
    e = BitVecVal(SBOX[255], 8)
    for i in range(254, -1, -1):
        e = If(x == i, BitVecVal(SBOX[i], 8), e)
    return e

def rol3(v):
    if isinstance(v, int):
        v &= 0xff
        return ((v<<3)|(v>>5)) & 0xff
    return RotateLeft(v, 3)

def xor(a,b):
    if isinstance(a,int) and isinstance(b,int): return (a^b)&0xff
    return a ^ b

def to32(v):  # extend 8-bit (int or bv8) to 32-bit int/bv
    if isinstance(v,int): return v & 0xff
    return ZeroExt(24, v)

def run_symbolic(inp):
    # inp: list of 32 values, each int (concrete) or BitVec8 (symbolic)
    fnv = 0x811c9dc5   # start concrete; becomes bv when it meets symbolic
    key = 0x42
    i = 0
    def mul(a):
        if isinstance(a,int): return (a * 0x01000193) & 0xffffffff
        return a * BitVecVal(0x01000193,32)
    def xor32(a,b):
        if isinstance(a,int) and isinstance(b,int): return (a^b)&0xffffffff
        aa = a if not isinstance(a,int) else BitVecVal(a,32)
        bb = b if not isinstance(b,int) else BitVecVal(b,32)
        return aa ^ bb
    for rnd in range(16):
        s0 = inp[i]
        s2 = inp[i+1] if i+1 <= 31 else 0
        s5 = rol3(key)
        s4 = xor(SB(xor(s2, s5)), s0)
        s0 = s2; s2 = s4
        s5 = xor(key, i & 0xff)
        s4 = xor(SB(xor(s2, s5)), s0)
        s0 = s2; s2 = s4
        # fnv = ((s0 ^ fnv)*p ^ (s2<<8 | i)) * p
        e = xor32(to32(s0), fnv)
        e = mul(e)
        cc_low = i & 0xff
        s2_32 = to32(s2)
        if isinstance(s2_32,int):
            cc = ((s2_32<<8) | cc_low) & 0xffffffff
        else:
            cc = ((s2_32 << 8) | cc_low)
        e = mul(xor32(e, cc))
        fnv = e
        key = xor(s0, s2)
        i += 2
    return fnv

def solve(free, fixedmap, timeout_ms=0):
    s = Solver()
    if timeout_ms:
        s.set("timeout", timeout_ms)
    inp = []
    for i in range(32):
        if i in fixedmap:
            inp.append(fixedmap[i])           # concrete int
        else:
            v = BitVec(f"in_{i}",8)
            s.add(v>=0x20, v<=0x7e)
            inp.append(v)
    fnv = run_symbolic(inp)
    if isinstance(fnv,int):
        print("all-concrete fnv", hex(fnv)); return None
    s.add(fnv == 0x86d03165)
    r = s.check()
    if r==sat:
        m=s.model()
        out=bytearray()
        for i in range(32):
            if i in fixedmap: out.append(fixedmap[i])
            else: out.append(m[inp[i]].as_long())
        return bytes(out)
    print("check:", r)
    return None

fixed={}
for i,ch in enumerate(b"IATCQ{"): fixed[i]=ch
fixed[31]=ord('}')
for i in range(6,26): fixed[i]=ord('A')   # fill 6..25 with 'A'
free=list(range(26,31))                    # 26,27,28,29,30 free (5 bytes)
t=time.time()
out=solve(free, fixed)
print(f"{time.time()-t:.1f}s")
if out:
    ok,_,fv=emu.run2(out)
    print("KEY:", out.decode('latin1','replace'), "ok:", ok, hex(fv))
