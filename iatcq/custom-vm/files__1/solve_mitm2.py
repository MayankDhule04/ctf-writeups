import importlib.util
spec=importlib.util.spec_from_file_location("emu2", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate2.py")
emu=importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

PRINT=[c for c in range(0x20,0x7f) if c!=ord('}')]

# Real MITM: fix bytes 6..27 (readable), then brute the free positions 28,29,30 (3 bytes) but
# 3 bytes over 95 alphabet = 857k which is <2^32 so expected 0 hits. Need >=5 free bytes for a hit.
# So: keep 6..25 fixed readable, free 26,27,28,29,30 (5 bytes, 95^5=7.7e9 > 2^32 -> ~1.8 hits).
# Brute 26,27 in python (outer), MITM the FNV over 28,29,30 is overkill; just brute 5 bytes with
# a fast forward-only check: precompute state after processing bytes 0..25 once (constant), then
# only rounds 13,14,15 depend on free bytes 26..31. But rounds also chain key. Round r consumes
# input[2r],[2r+1]; byte 26 -> round 13 (bytes 26,27), round 14 (28,29), round 15 (30,31).
# So free bytes 26..30 (+fixed '}') only affect rounds 13,14,15. Precompute up to round 13 start.

import numpy as np
img=open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\bss_img.bin","rb").read()
BASE=0x4060
PROG=img[0:0x60]; SBOX=list(img[0x40c0-BASE:0x40c0-BASE+256])
P=0x01000193; TARGET=0x86d03165
def rol8(v): v&=0xff; return ((v<<3)|(v>>5))&0xff

def run_upto(inp, upto_pc_rounds):
    # generic emulator but stop is by counter; we just run full and read—simpler: full run returns fv.
    ok,st,fv=emu.run(inp); return ok,fv

# Since only last 3 rounds depend on bytes>=26, precompute (fnv,key,state) at entry to processing byte26.
# Easiest: run emulator but capture state when state[1]==26. Patch a capture.
def run_capture(inp):
    state=[0]*16; fnv=0x811c9dc5; eq=0; pc=0; cap=None
    while pc<=0x5c:
        op=PROG[pc]; a1=PROG[pc+1]; a2=PROG[pc+2]
        if op==0xB2: state[a1]=a2&0xff; pc+=3
        elif op==0xA7: state[a1]=state[a2]; pc+=3
        elif op==0xA1:
            idx=state[a2]; state[a1]=inp[idx] if idx<=0x1f else 0; pc+=3
        elif op==0xE5: state[a1]=rol8(state[a1]); pc+=3
        elif op==0xC3:
            c=state[a1]; a=state[a2]; eq=1 if (c&0xff)==(a&0xff) else 0; state[a1]=(c^a)&0xff; pc+=3
        elif op==0xB6: state[a1]=SBOX[state[a1]]; pc+=3
        elif op==0xD4: state[a1]=(state[a1]+a2)&0xff; pc+=3
        elif op==0x17:
            pc+=3
            if eq==0: pc=a1
        elif op==0xF6:
            e=state[a1]^fnv; e&=0xffffffff; e=(e*P)&0xffffffff
            cc=(state[a2]<<8)&0xffffffff; cc|=state[1]; e^=cc; e=(e*P)&0xffffffff; fnv=e; pc+=3
        elif op==0xE9:
            return state[1]==0x20 and fnv==TARGET, fnv
        elif op==0xFF: break
        else: break
    return False,fnv

# Just brute 5 free bytes 26..30 with numpy-free python but only re-running full emulator is 7.7e9 (too slow).
# Instead brute bytes 26,27,28 in python(857k) each full-run ~ too slow in pure py.
# Compromise: brute 26,27 (9025) outer, and for inner 28,29,30 also full-run => 9025*857k huge. NO.
# Better: accept ANY printable collision via wide sweep on 4 bytes using the emulator vectorization we had.
# Reuse solve_np-style: but that needs numpy port of THIS PROG. Do it:

SB=np.frombuffer(bytes(SBOX),dtype=np.uint8).astype(np.uint32)
def rol3v(v): return ((v<<np.uint32(3))|(v>>np.uint32(5)))&np.uint32(0xff)
def mul(x): return ((x.astype(np.uint64)*np.uint64(P))&np.uint64(0xffffffff)).astype(np.uint32)

# Round function derived from PROG (matches emulate2). Encode 16 rounds; we vectorize last 3.
def round_scalar(a,b,key,i,h):
    # replicate emulate2 exact op sequence for one round consuming (a,b) at counter i, key=state[3]
    st=[0]*16
    # This is fragile; instead reuse run_capture-like single round by calling emulator on crafted? 
    # Simpler: derive from emulate2 semantics we already trust:
    s0=a
    s4=(i+1)&0xff  # state4=i, +1
    s2=b           # input[i+1]
    s5=rol8(key)
    s4=SBOX[(s2^s5)&0xff]^s0
    s0=s2; s2=s4
    s5=key^(i&0xff)
    s4=SBOX[(s2^s5)&0xff]^s0
    s0=s2; s2=s4
    e=((s0^h)&0xffffffff)*P & 0xffffffff
    cc=((s2<<8)|(i&0xff))&0xffffffff
    h2=((e^cc)&0xffffffff)*P & 0xffffffff
    key2=(s0^s2)&0xff
    return key2,h2

# sanity vs emulator on A*32
def full_scalar(inp):
    h=0x811c9dc5; key=0x42; i=0
    for r in range(16):
        key,h=round_scalar(inp[i],inp[i+1],key,i,h); i+=2
    return h
ta=b"A"*32
ok,st,fva=emu.run(ta)
print("emu",hex(fva),"scalar",hex(full_scalar(ta)),"match",fva==full_scalar(ta))
