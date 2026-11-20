img=open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\bss_img.bin","rb").read()
BASE=0x4060; PROG=img[0:0x60]; SBOX=list(img[0x40c0-BASE:0x40c0-BASE+256])
def rol8(v): v&=0xff; return ((v<<3)|(v>>5))&0xff

def run(inp, trace=False):
    state=[0]*16; fnv=0x811c9dc5; eq=0; pc=0; steps=0; loops=0
    while pc<=0x5c:
        op=PROG[pc]; a1=PROG[pc+1]; a2=PROG[pc+2]
        if op==0x17:
            # log the eq flag and state at the branch
            if trace: print(f"  [17] pc={pc:02x} eq={eq} state1={state[1]:#x} state5={state[5]:#x} -> {'continue' if eq else 'jump '+hex(a1)}")
            pc+=3
            if eq==0: pc=a1
            loops+=1
            continue
        if op==0xB2: state[a1]=a2&0xff; pc+=3
        elif op==0xA7: state[a1]=state[a2]; pc+=3
        elif op==0xA1:
            idx=state[a2]; state[a1]=inp[idx] if idx<=0x1f else 0; pc+=3
        elif op==0xE5: state[a1]=rol8(state[a1]); pc+=3
        elif op==0xC3:
            c=state[a1]; a=state[a2]; eq=1 if (c&0xff)==(a&0xff) else 0; state[a1]=(c^a)&0xff; pc+=3
        elif op==0xB6: state[a1]=SBOX[state[a1]]; pc+=3
        elif op==0xD4: state[a1]=(state[a1]+a2)&0xff; pc+=3
        elif op==0xF6:
            e=state[a1]^fnv; e&=0xffffffff; e=(e*0x01000193)&0xffffffff
            cc=(state[a2]<<8)&0xffffffff; cc|=state[1]; e^=cc; e=(e*0x01000193)&0xffffffff; fnv=e; pc+=3
        elif op==0xE9:
            return (state[1]==0x20 and fnv==0x86d03165), state, fnv, loops
        elif op==0xFF: break
        steps+=1
        if steps>3000: print("runaway"); break
    return False,state,fnv,loops

for tag,s in [("A*32",b"A"*32),("flagish",b"IATCQ{"+b"B"*25+b"}")]:
    print(tag)
    ok,st,fv,loops=run(s, trace=True)
    print(f"  => ok={ok} fnv={fv:08x} loops={loops} state1={st[1]:#x}\n")
