img=open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\bss_img.bin","rb").read()
BASE=0x4060
PROG = img[0x4060-BASE : 0x4060-BASE+0x60]   # program bytes, pc 0..0x5c
SBOX = list(img[0x40c0-BASE : 0x40c0-BASE+256])
print("PROG(%d):"%len(PROG), PROG.hex())
print("sbox ok", SBOX[0]==0x63 and SBOX[255]==0x16)

def rol8(v,n): v&=0xff; return ((v<<n)|(v>>(8-n)))&0xff

def run(inp, trace=False):
    state=[0]*16; fnv=0x811c9dc5; eq=0; pc=0; steps=0
    while pc<=0x5c:
        op=PROG[pc]; a1=PROG[pc+1]; a2=PROG[pc+2]
        if trace: print(f"pc={pc:02x} op={op:02x} {a1} {a2} st={bytes(state).hex()} fnv={fnv:08x}")
        if op==0xB2: state[a1]=a2&0xff; pc+=3
        elif op==0xA7: state[a1]=state[a2]; pc+=3
        elif op==0xA1:
            idx=state[a2]; state[a1]=inp[idx] if idx<=0x1f else 0; pc+=3
        elif op==0xE5: state[a1]=rol8(state[a1],3); pc+=3
        elif op==0xC3:
            c=state[a1]; a=state[a2]; eq=1 if (c&0xff)==(a&0xff) else 0; state[a1]=(c^a)&0xff; pc+=3
        elif op==0xB6: state[a1]=SBOX[state[a1]]; pc+=3
        elif op==0xD4: state[a1]=(state[a1]+a2)&0xff; pc+=3
        elif op==0x17:
            pc+=3
            if eq==0: pc=a1
        elif op==0xF6:
            e=state[a1]^fnv; e&=0xffffffff; e=(e*0x01000193)&0xffffffff
            cc=(state[a2]<<8)&0xffffffff; cc|=state[1]; e^=cc; e=(e*0x01000193)&0xffffffff; fnv=e; pc+=3
        elif op==0xE9:
            pc+=3; return (state[1]==0x20 and fnv==0x86d03165), state, fnv
        elif op==0xFF: break
        else: print("UNK",hex(op),"@",hex(pc)); break
        steps+=1
        if steps>2000: print("runaway"); break
    return False, state, fnv

if __name__=="__main__":
    ok,st,fv=run(b"A"*32)
    print("A*32 ->", ok, hex(fv))
