import ctypes, os, struct

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
# Breakpoint right at call to 0x402080 (0x403493) to capture args rdi,rsi,rdx,rcx,r8,r9 and stack args
BREAK1 = 0x403493
# Breakpoint inside gear_round right before call 0x401e30 (0x401fad) to see rdi,rsi,rdx,rcx args to linear_layer
BREAK2 = 0x401fad
# Breakpoint at entry of linear_layer 0x401e30 (right after push, to read args before they're clobbered) -- use 0x401e30 itself
BREAK3 = 0x401e30

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
    breaks = [BREAK1, BREAK3]
    orig={a:peek(pid,a,1) for a in breaks}
    for a in breaks: poke(pid,a,b'\xcc')
    hits=0
    seen3 = 0
    while hits < 4 and seen3 < 2:
        pt(PTRACE_CONT,pid,None,None)
        _,status=os.waitpid(pid,0)
        if os.WIFEXITED(status):
            print("exited"); break
        regs=getregs(pid); ha=regs.rip-1
        if ha==BREAK1:
            print("=== at call 0x402080 ===")
            print("rdi(fwd_sbox)=",hex(regs.rdi))
            print("rsi(inv_sbox)=",hex(regs.rsi))
            print("rdx(matrix)  =",hex(regs.rdx))
            print("rcx(arg4)    =",hex(regs.rcx))
            print("r8 (plaintext ptr) =",hex(regs.r8))
            print("r9 (arg6?)   =",hex(regs.r9))
            pt_buf = peek(pid, regs.r8, 32)
            print("  plaintext(32B) at r8:", pt_buf.hex())
            arg4_buf = peek(pid, regs.rcx, 32)
            print("  *rcx (first 32B):", arg4_buf.hex())
            # stack args: at this point rsp has the two just-pushed values (r14, then 0x10(rsp) copy) still on stack
            stack0 = struct.unpack('<Q', peek(pid, regs.rsp, 8))[0]
            stack1 = struct.unpack('<Q', peek(pid, regs.rsp+8, 8))[0]
            print("  stack arg0 (top):", hex(stack0))
            print("  stack arg1:", hex(stack1))
            poke(pid,ha,orig[ha]); regs.rip=ha; setregs(pid,regs)
            pt(PTRACE_SINGLESTEP,pid,None,None); os.waitpid(pid,0)
            poke(pid,ha,b'\xcc')
            hits+=1
        elif ha==BREAK3:
            seen3 += 1
            print(f"=== at linear_layer entry (call #{seen3}) ===")
            print("rdi(matrix)=",hex(regs.rdi))
            print("rsi(whiten_src)=",hex(regs.rsi))
            print("rdx(sub1_buf)=",hex(regs.rdx))
            print("rcx(out_ptr_holder)=",hex(regs.rcx))
            whiten = peek(pid, regs.rsi, 32)
            sub1 = peek(pid, regs.rdx, 32)
            print("  *rsi (whiten source, 32B):", whiten.hex())
            print("  *rdx (sub1 buf, 32B):", sub1.hex())
            poke(pid,ha,orig[ha]); regs.rip=ha; setregs(pid,regs)
            pt(PTRACE_SINGLESTEP,pid,None,None); os.waitpid(pid,0)
            if seen3 < 2:
                poke(pid,ha,b'\xcc')
            hits+=1
    try:
        pt(PTRACE_CONT,pid,None,None)
        os.waitpid(pid,0)
    except Exception:
        pass
