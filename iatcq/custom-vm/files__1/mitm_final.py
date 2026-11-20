import numpy as np, importlib.util
spec=importlib.util.spec_from_file_location("emu2", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate2.py")
emu=importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

img=open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\bss_img.bin","rb").read()
BASE=0x4060; SBOX=list(img[0x40c0-BASE:0x40c0-BASE+256])
P=0x01000193; MASK=0xffffffff; TARGET=0x86d03165
SBv=np.frombuffer(bytes(SBOX),dtype=np.uint8).astype(np.uint32)

def rol8(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
def round_scalar(a,b,key,i,h):
    s0=a; s2=b
    s5=rol8(key); s4=SBOX[(s2^s5)&0xff]^s0; s0=s2; s2=s4
    s5=key^(i&0xff); s4=SBOX[(s2^s5)&0xff]^s0; s0=s2; s2=s4
    e=((s0^h)&MASK)*P & MASK
    cc=((s2<<8)|(i&0xff))&MASK
    h2=((e^cc)&MASK)*P & MASK
    return (s0^s2)&0xff, h2

# vectorized single round: a,b arrays; key,h arrays; i scalar
def rol8v(v): return ((v<<np.uint32(3))|(v>>np.uint32(5)))&np.uint32(0xff)
def mul(x): return ((x.astype(np.uint64)*np.uint64(P))&np.uint64(MASK)).astype(np.uint32)
def round_vec(a,b,key,h,i):
    s0=a & np.uint32(0xff); s2=b & np.uint32(0xff)
    s5=rol8v(key)
    s4=(SBv[(s2 ^ s5)&np.uint32(0xff)] ^ s0)&np.uint32(0xff)
    s0=s2; s2=s4
    s5=(key ^ np.uint32(i&0xff))&np.uint32(0xff)
    s4=(SBv[(s2 ^ s5)&np.uint32(0xff)] ^ s0)&np.uint32(0xff)
    s0=s2; s2=s4
    e=mul(s0 ^ h)
    cc=((s2<<np.uint32(8)) | np.uint32(i&0xff))&np.uint32(MASK)
    h2=mul(e ^ cc)
    key2=(s0 ^ s2)&np.uint32(0xff)
    return key2,h2

PR=[c for c in range(0x20,0x7f) if c!=ord('}')]

# fix prefix + filler for bytes 0..25, compute (key,h) at entry of round 13 via emulator-consistent scalar
inp=bytearray(b"IATCQ{"+b"_"*25+b"}")
# compute state up to processing byte index 26 (rounds 0..12) with scalar rounds
def prefix_state(inp):
    h=0x811c9dc5; key=0x42; i=0
    for r in range(13):   # rounds 0..12 consume bytes 0..25
        key,h=round_scalar(inp[i],inp[i+1],key,i,h); i+=2
    return key,h  # entry to round13, i=26
key13,h13=prefix_state(inp)
print("key13",hex(key13),"h13",hex(h13))

# Forward enumerate b26,b27,b28,b29 -> after round14 (key14,h14). Then round15 with (b30,'}').
# We want final==TARGET. Enumerate b26,b27 (scalar, 95^2) -> (key14a,h14a) after round13, then
# vectorize b28,b29 for round14, then b30 for round15.
B=np.array(PR,dtype=np.uint32)
close=np.uint32(ord('}'))
found=None
for b26 in PR:
    for b27 in PR:
        k14,h14 = round_scalar(b26,b27,key13,26,h13)  # after round13
        # round14 vectorized over b28(=A),b29(=Bb)
        A,Bb=np.meshgrid(B,B,indexing='ij'); A=A.ravel(); Bb=Bb.ravel()
        k15,h15 = round_vec(A,Bb,np.uint32(k14)*np.ones_like(A),np.uint32(h14)*np.ones_like(A),28)
        # round15 over b30 (=C), b31='}'
        for c30 in PR:
            kf,hf = round_vec(np.uint32(c30)*np.ones_like(A), close*np.ones_like(A), k15, h15, 30)
            hit=np.where(hf==np.uint32(TARGET))[0]
            if hit.size:
                idx=hit[0]
                b28=int(A[idx]); b29=int(Bb[idx])
                out=bytearray(inp); out[26]=b26; out[27]=b27; out[28]=b28; out[29]=b29; out[30]=c30; out[31]=ord('}')
                found=bytes(out); break
        if found: break
    if found: break

if found:
    ok,st,fv=emu.run(found)
    print("KEY:", found.decode('latin1'))
    print("emulator ACCESS GRANTED:", ok, "fnv", hex(fv))
    open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\MITM_KEY.txt","w").write(found.decode('latin1'))
else:
    print("no hit")
