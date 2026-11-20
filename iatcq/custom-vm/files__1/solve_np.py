import numpy as np, importlib.util, itertools, time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = np.frombuffer(prog_full[:256], dtype=np.uint8).astype(np.uint32)
SBOX_i = list(prog_full[:256])
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

P = np.uint64(0x01000193)
MASK = np.uint64(0xffffffff)
TARGET = 0x86d03165

def rol3_i(v): v&=0xff; return ((v<<3)|(v>>5))&0xff

def round_scalar(a,b,key,i,h):
    t1 = SBOX_i[(b ^ rol3_i(key)) & 0xff] ^ a
    t2 = SBOX_i[(t1 ^ (key ^ i)) & 0xff] ^ b
    e = ((t1 ^ h) * 0x01000193) & 0xffffffff
    cc = ((t2 << 8) | (i & 0xff)) & 0xffffffff
    h2 = ((e ^ cc) * 0x01000193) & 0xffffffff
    return (t1 ^ t2) & 0xff, h2

# fixed input
inp = bytearray(b"IATCQ{" + b"A"*(26-6) + b"}")   # 6 + 20 + 1 = 27? fix below
inp = bytearray(32)
inp[0:6] = b"IATCQ{"
for i in range(6,31): inp[i]=ord('A')
inp[31]=ord('}')

# precompute rounds 0..12 (uses in[0..25]) -> k13,h13
h=0x811c9dc5; key=0x42
for r in range(13):
    a=inp[2*r]; b=inp[2*r+1]
    key,h = round_scalar(a,b,key,2*r,h)
k13,h13 = key,h
print("k13",hex(k13),"h13",hex(h13))

rng = np.arange(0x20,0x7f, dtype=np.uint32)  # printable 0x20..0x7e (95)
# vector grid for in28,in29,in30
A28,A29,A30 = np.meshgrid(rng,rng,rng, indexing='ij')
A28=A28.ravel(); A29=A29.ravel(); A30=A30.ravel()
B31 = np.uint32(ord('}'))

def rol3v(v): return ((v<<np.uint32(3))|(v>>np.uint32(5))) & np.uint32(0xff)
def mul(x): return ((x.astype(np.uint64)*P)&MASK).astype(np.uint32)

t0=time.time()
found=None
for c26 in range(0x20,0x7f):
    for c27 in range(0x20,0x7f):
        # round 13 scalar: a=in26=c26,b=in27=c27,key=k13,i=26,h=h13
        k14,h14 = round_scalar(c26,c27,k13,26,h13)
        # round 14 vector: a=A28,b=A29,key=k14,i=28,h=h14
        t1 = SBOX[(A29 ^ rol3v(np.uint32(k14))) & np.uint32(0xff)] ^ A28
        t1 &= np.uint32(0xff)
        t2 = SBOX[(t1 ^ np.uint32(k14 ^ 28)) & np.uint32(0xff)] ^ A29
        t2 &= np.uint32(0xff)
        e = mul(t1 ^ np.uint32(h14))
        cc = ((t2 << np.uint32(8)) | np.uint32(28)) & np.uint32(0xffffffff)
        h15 = mul(e ^ cc)
        k15 = (t1 ^ t2) & np.uint32(0xff)
        # round 15 vector: a=A30,b='}',key=k15,i=30,h=h15
        t1b = SBOX[(B31 ^ rol3v(k15)) & np.uint32(0xff)] ^ A30
        t1b &= np.uint32(0xff)
        t2b = SBOX[(t1b ^ (k15 ^ np.uint32(30))) & np.uint32(0xff)] ^ B31
        t2b &= np.uint32(0xff)
        e2 = mul(t1b ^ h15)
        cc2 = ((t2b << np.uint32(8)) | np.uint32(30)) & np.uint32(0xffffffff)
        h16 = mul(e2 ^ cc2)
        hit = np.where(h16 == np.uint32(TARGET))[0]
        if hit.size:
            idx=hit[0]
            found=(c26,c27,int(A28[idx]),int(A29[idx]),int(A30[idx]))
            break
    if found: break
print(f"search {time.time()-t0:.1f}s found={found}")
if found:
    inp[26],inp[27],inp[28],inp[29],inp[30]=found
    out=bytes(inp)
    ok,_,fv=emu.run2(out)
    print("KEY:", out.decode('latin1','replace'), "ACCESS GRANTED:", ok, hex(fv))
    open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\FOUND_KEY.txt","wb").write(out)
else:
    print("no solution in 5-byte tail space; expand needed")
