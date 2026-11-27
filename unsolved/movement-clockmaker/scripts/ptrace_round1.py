import ctypes, os

libc = ctypes.CDLL("libc.so.6", use_errno=True)
PTRACE_TRACEME=0; PTRACE_CONT=7; PTRACE_SINGLESTEP=9; PTRACE_GETREGS=12; PTRACE_SETREGS=13
class R(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in [
        "r15","r14","r13","r12","rbp","rbx","r11","r10","r9","r8",
        "rax","rcx","rdx","rsi","rdi","orig_rax","rip","cs","eflags",
        "rsp","ss","fs_base","gs_base","ds","es","fs","gs"]]
libc.ptrace.restype=ctypes.c_long
libc.ptrace.argtypes=[ctypes.c_long,ctypes.c_long,ctypes.c_void_p,ctypes.c_void_p]
def pt(req,pid,addr,data): return libc.ptrace(req,pid,addr,data)
def getregs(pid):
    r=R(); pt(PTRACE_GETREGS,pid,None,ctypes.byref(r)); return r
def setregs(pid,r): pt(PTRACE_SETREGS,pid,None,ctypes.byref(r))
def peek(pid,addr,n):
    with open(f"/proc/{pid}/mem","rb") as f: f.seek(addr); return f.read(n)
def poke(pid,addr,data):
    with open(f"/proc/{pid}/mem","r+b") as f: f.seek(addr); f.write(data)

BIN=os.path.abspath("movement_patched2")
# gear_round(0x401f50) args: rdi=fwd_sbox rsi=inv_sbox rdx=matrix rcx=whiten_const r8=input_ptr r9=output_ptr
ENTRY = 0x401f50
AFTER_SUB1 = 0x401f9d   # just after forward-sub loop; sub1 buffer at rsp+0x10 (local, relative -- need rsp at this point)
AFTER_LINEAR = 0x401fb2  # right after call 0x401e30 returns; perm at rsp+0x30
AFTER_ROUND = 0x401fde  # near end, after inverse-sub loop writes result to r9(output_ptr) -- use the ret addr area; actually just break at 0x401fde (add $0x38,%rsp already executed at prior insn? check) use 0x401fdc+2=0x401fde is after jne, before epilogue pops -- rsp still has frame

payload = b"ctf7{" + b"X"*53 + b"}"
r_in, w_in = os.pipe()
os.write(w_in, payload + b"\n")
os.close(w_in)
pid=os.fork()
if pid==0:
    pt(PTRACE_TRACEME,0,None,None)
    os.dup2(r_in,0)
    os.execv(BIN,[BIN]); os._exit(1)
else:
    os.waitpid(pid,0)
    poke(pid, ENTRY, b'\xcc')
    orig_entry = None
    pt(PTRACE_CONT,pid,None,None)
    _,status=os.waitpid(pid,0)
    regs=getregs(pid)
    ha = regs.rip-1
    assert ha==ENTRY, hex(ha)
    input_ptr = regs.r8
    output_ptr = regs.r9
    fwd_ptr = regs.rdi
    inv_ptr = regs.rsi
    whiten_ptr = regs.rcx
    state0 = peek(pid, input_ptr, 32)
    print("state0 (input to round1):", state0.hex())
    print("whiten buf:", peek(pid, whiten_ptr, 32).hex())
    # restore byte, step off breakpoint
    orig = peek(pid, ENTRY, 1)
    # we already overwrote; need original byte -- re-read binary file instead
    with open(BIN,'rb') as f:
        f.seek(ENTRY - 0x400000)
        orig_byte = f.read(1)
    poke(pid, ENTRY, orig_byte)
    regs.rip = ENTRY
    setregs(pid, regs)

    for addr in [AFTER_SUB1, AFTER_LINEAR]:
        with open(BIN,'rb') as f:
            f.seek(addr - 0x400000)
            ob = f.read(1)
        poke(pid, addr, b'\xcc')
        pt(PTRACE_CONT,pid,None,None)
        _,status=os.waitpid(pid,0)
        regs2 = getregs(pid)
        hb = regs2.rip-1
        print("hit", hex(hb), "rsp=", hex(regs2.rsp))
        if hb == AFTER_SUB1:
            sub1 = peek(pid, regs2.rsp+0x10, 32)
            print("sub1:", sub1.hex())
        elif hb == AFTER_LINEAR:
            perm = peek(pid, regs2.rsp+0x10, 32)
            print("perm (at rsp+0x10, in-place over sub1):", perm.hex())
        poke(pid, hb, ob)
        regs2.rip = hb
        setregs(pid, regs2)

    # continue to see final output after round1 (output_ptr)
    # break at 0x401fde (just after inverse-sub loop completes before epilogue)
    FIN = 0x401fde
    with open(BIN,'rb') as f:
        f.seek(FIN - 0x400000)
        ob2 = f.read(1)
    poke(pid, FIN, b'\xcc')
    pt(PTRACE_CONT,pid,None,None)
    _,status=os.waitpid(pid,0)
    regs3 = getregs(pid)
    hb3 = regs3.rip-1
    print("hit", hex(hb3))
    out = peek(pid, output_ptr, 32)
    print("round1 output:", out.hex())
