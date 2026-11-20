from z3 import *
import importlib.util, time, sys

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

def SB(x):
    if isinstance(x,int): return SBOX[x&0xff]
    e = BitVecVal(SBOX[255],8)
    for i in range(254,-1,-1):
        e = If(x==i, BitVecVal(SBOX[i],8), e)
    return e
def rol3(v):
    if isinstance(v,int): v&=0xff; return ((v<<3)|(v>>5))&0xff
    return RotateLeft(v,3)
def xor(a,b):
    if isinstance(a,int) and isinstance(b,int): return (a^b)&0xff
    return a^b
def to32(v): return (v&0xff) if isinstance(v,int) else ZeroExt(24,v)

def run(inp):
    fnv=0x811c9dc5; key=0x42; i=0
    def mul(a): return (a*0x01000193)&0xffffffff if isinstance(a,int) else a*BitVecVal(0x01000193,32)
    def x32(a,b):
        if isinstance(a,int) and isinstance(b,int): return (a^b)&0xffffffff
        aa=a if not isinstance(a,int) else BitVecVal(a,32)
        bb=b if not isinstance(b,int) else BitVecVal(b,32)
        return aa^bb
    for rnd in range(16):
        s0=inp[i]; s2=inp[i+1] if i+1<=31 else 0
        s5=rol3(key); s4=xor(SB(xor(s2,s5)),s0); s0=s2; s2=s4
        s5=xor(key,i&0xff); s4=xor(SB(xor(s2,s5)),s0); s0=s2; s2=s4
        e=mul(x32(to32(s0),fnv))
        s2e=to32(s2)
        cc=(((s2e<<8)|(i&0xff))&0xffffffff) if isinstance(s2e,int) else ((s2e<<8)|(i&0xff))
        fnv=mul(x32(e,cc)); key=xor(s0,s2); i+=2
    return fnv

fixed={}
for i,ch in enumerate(b"IATCQ{"): fixed[i]=ch
fixed[31]=ord('}')

s=Solver()
s.set("timeout", 1200000)  # 20 min
inp=[]
for i in range(32):
    if i in fixed:
        inp.append(fixed[i])
    else:
        v=BitVec(f"in_{i}",8)
        s.add(v>=0x20, v<=0x7e)   # printable
        inp.append(v)
fnv=run(inp)
s.add(fnv==0x86d03165)
print("built, checking...", flush=True)
t=time.time(); r=s.check(); print("RESULT", r, f"{time.time()-t:.1f}s", flush=True)
if r==sat:
    m=s.model()
    out=bytes(fixed[i] if i in fixed else m[inp[i]].as_long() for i in range(32))
    ok,_,fv=emu.run2(out)
    print("KEY:", out.decode('latin1','replace'), flush=True)
    print("emulator ACCESS GRANTED:", ok, hex(fv), flush=True)
    open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\FOUND_KEY.txt","wb").write(out)
