#!/usr/bin/env python3
import wave, struct, random, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
w=wave.open("/work/noise.wav"); n=w.getnframes()
u=[x & 0xFFFF for x in struct.unpack("<%dh"%n, w.readframes(n))]
import numpy as np
U=np.array(u,dtype=np.uint16)

def extract_and_show(prng_u16, ignore_bit):
    ks=[(v>>ignore_bit)&1 for v in prng_u16]
    bits=[((u[i]>>ignore_bit)&1)^ks[i] for i in range(len(prng_u16))]
    out=bytearray()
    for j in range(0,min(len(bits),4000)-7,8):
        val=0
        for k in range(8): val=(val<<1)|bits[j+k]
        out.append(val)
    print("   extracted:", bytes(out[:80]))

# ---- numpy brute (fast, vectorized check on first samples) ----
CHK=40
tgt_hi = U[:CHK] >> 1
found=False
for ib in (0,15):
    tgt = (U[:CHK] >> 1) if ib==0 else (U[:CHK] & 0x7FFF)  # ignore that bit
    mask = (0xFFFF ^ (1<<ib))
    tgtm = (U[:CHK] & mask)
    for seed in range(0, 1<<21):
        rng=np.random.RandomState(seed)
        a=rng.randint(0,65536,CHK).astype(np.uint16)
        if np.array_equal(a & mask, tgtm):
            print(f"NUMPY RandomState seed={seed} ignore_bit={ib}")
            full=np.random.RandomState(seed).randint(0,65536,n).astype(np.uint16)
            extract_and_show(list(full), ib); found=True; break
    if found: break
if not found: print("numpy RandomState: no seed <2^21")
