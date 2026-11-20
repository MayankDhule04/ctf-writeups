from pwn import *
from capstone import *
e=ELF('chal',checksec=False)
md=Cs(CS_ARCH_X86,CS_MODE_64)
# scan all executable sections
interesting=[]
for sec in e.sections:
    if sec.header.sh_flags & 0x4:  # SHF_EXECINSTR
        data=sec.data(); base=sec.header.sh_addr
        # for each ret (c3) look back up to 12 bytes and disasm
        for i,b in enumerate(data):
            if b in (0xc3,):  # ret
                for back in range(1,16):
                    start=i-back
                    if start<0: break
                    insns=list(md.disasm(data[start:i+1], base+start))
                    if not insns: continue
                    # must end exactly at ret
                    if insns[-1].address==base+i and insns[-1].mnemonic=='ret':
                        seq=' ; '.join(f"{x.mnemonic} {x.op_str}".strip() for x in insns)
                        if any(k in seq for k in ['rdi','rsi','rdx','rax','leave','syscall','call','jmp']):
                            interesting.append((base+start,seq))
seen=set()
for a,s in interesting:
    if s in seen: continue
    seen.add(s)
    if any(k in s for k in ['pop rdi','pop rsi','pop rdx','pop rax','leave','syscall','mov rdi','mov rsi','call rax','jmp rax','call qword','mov edi']):
        print(hex(a),'|',s)
