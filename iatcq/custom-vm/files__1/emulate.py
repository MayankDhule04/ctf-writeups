prog_full = open(r"c:\Users\mayan\OneDrive\Desktop\ctf\custom_vm\prog.bin","rb").read()
SBOX = list(prog_full[:256])
PROG = prog_full  # program is indexed absolutely from prog start; instrs region begins at 0x100

def rol8(v, n):
    v &= 0xff
    return ((v << n) | (v >> (8 - n))) & 0xff

def run(inp, trace=False):
    assert len(inp) == 32
    state = [0]*16
    fnv = 0x811c9dc5
    eqflag = 0
    pc = 0x100  # rsi base is prog start; edx starts 0, but rsi=prog+0x100? check below
    # Actually rsi = rip+0x2bd1 = 0x4060 (bss decoded buffer). edx starts at 0.
    # The decoded buffer = 256 sbox + program. But dispatch reads prog[edx] with edx from 0.
    # However our PROG includes the sbox as first 256 bytes, and instrs start at 0x100.
    # The loop condition cmp edx,0x5c means edx in program-local coords starting 0 -> region is 0x00..0x5c
    # of the *instruction* stream, i.e. our bytes at 0x100.. . So use a separate instr array.
    raise SystemExit

# Reconsider: rsi points to the instruction stream (not including sbox). The sbox is a separate
# object at r9=rip+0x2b05. Let's slice instructions = PROG[0x100:].
INSTR = PROG[0x100:]

def run2(inp, trace=False):
    state = [0]*16
    fnv = 0x811c9dc5
    eqflag = 0
    pc = 0
    steps = 0
    while pc <= 0x5c:
        op = INSTR[pc]
        a1 = INSTR[pc+1]
        a2 = INSTR[pc+2]
        if trace:
            print(f"pc={pc:02x} op={op:02x} a1={a1} a2={a2} state={bytes(state).hex()} fnv={fnv:08x} eq={eqflag}")
        if op == 0xB2:      # LOAD imm
            state[a1] = a2 & 0xff; pc += 3
        elif op == 0xA7:    # MOV
            state[a1] = state[a2]; pc += 3
        elif op == 0xA1:    # LOAD input[state[a2]]
            idx = state[a2]
            state[a1] = inp[idx] if idx <= 0x1f else 0
            pc += 3
        elif op == 0xE5:    # ROL3
            state[a1] = rol8(state[a1], 3); pc += 3
        elif op == 0xC3:    # XOR + eqflag
            c = state[a1]; a = state[a2]
            eqflag = 1 if (c & 0xff) == (a & 0xff) else 0
            state[a1] = (c ^ a) & 0xff
            pc += 3
        elif op == 0xB6:    # SBOX
            state[a1] = SBOX[state[a1]]; pc += 3
        elif op == 0xD4:    # ADD imm
            state[a1] = (state[a1] + a2) & 0xff; pc += 3
        elif op == 0x17:    # COND: if eqflag continue else jump a1
            pc += 3
            if eqflag == 0:
                pc = a1
        elif op == 0xF6:    # FNV mix
            # eax = state[a1]; eax ^= fnv; eax *= 0x01000193
            # ecx = state[a2]; ecx <<=8; ecx |= state[1]; eax ^= ecx; eax*=0x01000193
            e = state[a1]
            e ^= fnv; e &= 0xffffffff
            e = (e * 0x01000193) & 0xffffffff
            cc = state[a2]
            cc = (cc << 8) & 0xffffffff
            cc |= state[1]
            e ^= cc
            e = (e * 0x01000193) & 0xffffffff
            fnv = e
            pc += 3
        elif op == 0xE9:    # FINAL
            pc += 3
            ok = (state[1] == 0x20) and (fnv == 0x86d03165)
            return ok, state, fnv
        elif op == 0xFF:
            break
        else:
            print("UNKNOWN op", hex(op), "at", hex(pc)); break
        steps += 1
        if steps > 1000: 
            print("runaway"); break
    return False, state, fnv

if __name__ == "__main__":
    print("SBOX ok:", SBOX[0]==0x63 and SBOX[1]==0x7c)
    print("INSTR:", INSTR[:0x60].hex())
    ok, st, fnv = run2(b"A"*32, trace=True)
    print("result", ok, bytes(st).hex(), hex(fnv))
