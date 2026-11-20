import numpy as np, importlib.util, time

prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = np.frombuffer(prog_full[:256], dtype=np.uint8).astype(np.uint32)
SBOX_i = list(prog_full[:256])
spec = importlib.util.spec_from_file_location("emu", r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\emulate.py")
emu = importlib.util.module_from_spec(spec); spec.loader.exec_module(emu)

P=np.uint64(0x01000193); MASK=np.uint64(0xffffffff); TARGET=0x86d03165
def rol3_i(v): v&=0xff; return ((v<<3)|(v>>5))&0xff
def round_scalar(a,b,key,i,h):
    t1=SBOX_i[(b^rol3_i(key))&0xff]^a
    t2=SBOX_i[(t1^(key^i))&0xff]^b
    e=((t1^h)*0x01000193)&0xffffffff
    cc=((t2<<8)|(i&0xff))&0xffffffff
    h2=((e^cc)*0x01000193)&0xffffffff
    return (t1^t2)&0xff,h2
def rol3v(v): return ((v<<np.uint32(3))|(v>>np.uint32(5)))&np.uint32(0xff)
def mul(x): return ((x.astype(np.uint64)*P)&MASK).astype(np.uint32)

# readable alphabet for body
ALPHA = [ord(c) for c in "abcdefghijklmnopqrstuvwxyz0123456789_"]
alpha = np.array(ALPHA, dtype=np.uint32)

def run_prefix(inp, upto_round):
    h=0x811c9dc5; key=0x42
    for r in range(upto_round):
        key,h=round_scalar(inp[2*r],inp[2*r+1],key,2*r,h)
    return key,h

# Template: IATCQ{ + 20 body + } ; body positions 6..25 (20 chars) then '}' at 31? 
# 6 + 25 + 1 = 32 => body is positions 6..30 (25 chars), '}' at 31.
# We'll fix body[0..19] (pos6..25) to a filler and brute pos 26..30 (5 chars) over ALPHA (37^5=69M).
# Vary filler to explore; collect ALL hits.

def search(fill_body20):
    inp=bytearray(32)
    inp[0:6]=b"IATCQ{"
    for k in range(20): inp[6+k]=fill_body20[k]
    inp[31]=ord('}')
    # rounds 0..12 use pos0..25 -> all fixed. round13 uses pos26,27 (brute), round14 pos28,29, round15 pos30,31
    key13,h13=run_prefix(inp,13)
    hits=[]
    # brute 26,27 scalar; 28,29,30 vector
    A28,A29,A30=np.meshgrid(alpha,alpha,alpha,indexing='ij')
    A28=A28.ravel();A29=A29.ravel();A30=A30.ravel()
    B31=np.uint32(ord('}'))
    for c26 in ALPHA:
        for c27 in ALPHA:
            k14,h14=round_scalar(c26,c27,key13,26,h13)
            t1=(SBOX[(A29^rol3v(np.uint32(k14)))&np.uint32(0xff)]^A28)&np.uint32(0xff)
            t2=(SBOX[(t1^np.uint32(k14^28))&np.uint32(0xff)]^A29)&np.uint32(0xff)
            e=mul(t1^np.uint32(h14)); cc=((t2<<np.uint32(8))|np.uint32(28))&np.uint32(0xffffffff)
            h15=mul(e^cc); k15=(t1^t2)&np.uint32(0xff)
            t1b=(SBOX[(B31^rol3v(k15))&np.uint32(0xff)]^A30)&np.uint32(0xff)
            t2b=(SBOX[(t1b^(k15^np.uint32(30)))&np.uint32(0xff)]^B31)&np.uint32(0xff)
            e2=mul(t1b^h15); cc2=((t2b<<np.uint32(8))|np.uint32(30))&np.uint32(0xffffffff)
            h16=mul(e2^cc2)
            idxs=np.where(h16==np.uint32(TARGET))[0]
            for idx in idxs:
                body=bytes(fill_body20)+bytes([c26,c27,int(A28[idx]),int(A29[idx]),int(A30[idx])])
                hits.append(b"IATCQ{"+body+b"}")
    return hits

t0=time.time()
allhits=[]
# try a handful of fillers; readable body likely words. Start with all 'a', then some english-ish.
fillers=[b"a"*20, b"custom_vm_reversing_", b"hyperstate_vm_crackm", b"reverse_the_custom_v"]
for f in fillers:
    f=(f+b"a"*20)[:20]
    hs=search(f)
    for h in hs:
        ok,_,fv=emu.run2(h)
        print("HIT", h.decode('latin1'), "verified", ok)
        allhits.append(h)
    print(f"filler {f} -> {len(hs)} hits  ({time.time()-t0:.1f}s)")
print("total", len(allhits))
