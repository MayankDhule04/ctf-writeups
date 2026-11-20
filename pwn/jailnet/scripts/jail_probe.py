#!/usr/bin/env python3
from pwn import remote, context
import time
context.log_level='error'
HOST="jailnet-4155a79b5812.chall.nnsc.tf"; PORT=1337

def run(form, wait=2.5):
    io=remote(HOST,PORT,ssl=True)
    time.sleep(0.6)
    try: io.recvuntil(b'sandbox> ', timeout=6)
    except: pass
    body=(form+"\n").encode()
    if len(body)<4096: body+=b" "*(4096-len(body))
    io.send(body)
    time.sleep(wait)
    data=b''
    t=time.time()
    while time.time()-t<wait+2:
        try:
            d=io.recv(timeout=1.5)
            if not d: break
            data+=d
        except: break
    io.close()
    return data.decode(errors='replace')

# candidate potentially-dangerous or useful symbols that might survive filtering
cands = [
    "slurp","spit","os/read","read","file/open","file/read","getline",
    "dofile","require","import","eval","eval-string","run-context",
    "marshal","unmarshal","native","ffi/native","asm","disasm",
    "os/execute","os/spawn","os/shell","os/getenv","os/environ",
    "dyn","setdyn","curenv","root-env","fiber/new","fiber/current",
    "debug/stack","in","get","put","invoke","apply","comp",
    "keys","values","pairs","table/proto-flatten","getproto","proto-view",
    "int/s64","peg/match","string/format","printf","pp",
    "load-image","make-image","parse","parse-all","tuple","struct",
    "resume","fiber","ev/read","net/read","module/find","module/cache",
]
alive=[]
for c in cands:
    out=run(f"(print (type {c}))")
    status = out.strip().split('\n')[0]
    print(f"{c:24s} -> {status[:60]}")
    if 'unknown symbol' not in out and status:
        alive.append((c,status))
print("\nALIVE:", [a[0] for a in alive])
