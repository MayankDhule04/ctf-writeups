import ctypes, os

libc = ctypes.CDLL("libc.so.6", use_errno=True)
PTRACE_TRACEME=0; PTRACE_CONT=7; PTRACE_GETREGS=12

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
def peek(pid,addr,n):
    with open(f"/proc/{pid}/mem","rb") as f: f.seek(addr); return f.read(n)
def poke(pid,addr,data):
    with open(f"/proc/{pid}/mem","r+b") as f: f.seek(addr); f.write(data)

BIN=os.path.abspath("movement")  # use the TRUE original, unpatched
BREAK = 0x40197b  # test %r9,%r9 -- read r9 right here (ptrace syscall result)

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
    with open(BIN,'rb') as f:
        f.seek(BREAK-0x400000); ob=f.read(1)
    poke(pid,BREAK,b'\xcc')
    pt(PTRACE_CONT,pid,None,None)
    _,status=os.waitpid(pid,0)
    regs=getregs(pid)
    r9 = regs.r9
    # sign-extend / interpret as signed 64
    r9_signed = r9 if r9 < (1<<63) else r9 - (1<<64)
    print("r9 (ptrace syscall return):", hex(r9), "signed:", r9_signed)
    print("edi before cmovs:", hex(regs.rdi))
    print("edx (xor 0x2aa variant):", hex(regs.rdx))
