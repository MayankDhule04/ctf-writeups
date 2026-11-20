import numpy as np, importlib.util, random
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
    e=((s0^h)&MASK)*P&MASK; cc=((s2<<8)|(i&0xff))&MASK; h2=((e^cc)&MASK)*P&MASK
    return (s0^s2)&0xff,h2
def rol8v(v): return ((v<<np.uint32(3))|(v>>np.uint32(5)))&np.uint32(0xff)
def mul(x): return ((x.astype(np.uint64)*np.uint64(P))&np.uint64(MASK)).astype(np.uint32)
def round_vec(a,b,key,h,i):
    s0=a&np.uint32(0xff); s2=b&np.uint32(0xff)
    s5=rol8v(key); s4=(SBv[(s2^s5)&np.uint32(0xff)]^s0)&np.uint32(0xff); s0=s2; s2=s4
    s5=(key^np.uint32(i&0xff))&np.uint32(0xff); s4=(SBv[(s2^s5)&np.uint32(0xff)]^s0)&np.uint32(0xff); s0=s2; s2=s4
    e=mul(s0^h); cc=((s2<<np.uint32(8))|np.uint32(i&0xff))&np.uint32(MASK); h2=mul(e^cc)
    return (s0^s2)&np.uint32(0xff),h2

ALNUM=[c for c in range(0x30,0x3a)]+[c for c in range(0x41,0x5b)]+[c for c in range(0x61,0x7b)]
B=np.array(ALNUM,dtype=np.uint32)

def prefix_state(inp):
    h=0x811c9dc5; key=0x42; i=0
    for r in range(13): key,h=round_scalar(inp[i],inp[i+1],key,i,h); i+=2
    return key,h

def solve_with_filler(fill):  # fill: 20-char bytes for positions 6..25
    inp=bytearray(b"IATCQ{"+bytes(fill)+b"\x00\x00\x00\x00\x00}")
    key13,h13=prefix_state(inp)
    A,Bb=np.meshgrid(B,B,indexing='ij'); A=A.ravel(); Bb=Bb.ravel()
    close=np.uint32(ord('}'))
    for b26 in ALNUM:
        for b27 in ALNUM:
            k14,h14=round_scalar(b26,b27,key13,26,h13)
            k15,h15=round_vec(A,Bb,np.full_like(A,k14),np.full_like(A,h14),28)
            for c30 in ALNUM:
                kf,hf=round_vec(np.full_like(A,c30),np.full_like(A,close),k15,h15,30)
                hit=np.where(hf==np.uint32(TARGET))[0]
                if hit.size:
                    idx=hit[0]
                    out=bytearray(inp); out[26]=b26;out[27]=b27;out[28]=int(A[idx]);out[29]=int(Bb[idx]);out[30]=c30;out[31]=ord('}')
                    return bytes(out)
    return None

random.seed(1)
keys=[]
words=[b"DarkCoverVMreverse00","CustomVMkeygenSolved","hiddenmachinequiet01","walkthrough32bytesok","zerosandonescoverdrk","spectral0verrideVMxx"]
tries=0
for w in words:
    fill=(w+b"____________________")[:20]
    fill=bytes(c if (0x30<=c<0x7b) else ord('X') for c in fill.replace(b"_",b"X"))
    out=solve_with_filler(fill)
    if out:
        ok,st,fv=emu.run(out)
        if ok:
            keys.append(out.decode('latin1'))
            print("KEY:", out.decode('latin1'), "ok", ok, hex(fv))
print("\nfound",len(keys),"keys")
