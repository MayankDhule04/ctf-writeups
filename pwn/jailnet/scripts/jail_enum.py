#!/usr/bin/env python3
from pwn import remote, context
import time
context.log_level='error'
HOST="jailnet-4155a79b5812.chall.nnsc.tf"; PORT=1337
def run(form, wait=2.0):
    io=remote(HOST,PORT,ssl=True)
    time.sleep(0.5)
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
            d=io.recv(timeout=1.2)
            if not d: break
            data+=d
        except: break
    io.close()
    return data.decode(errors='replace')

# Broad list of janet builtins to see what survived filtering
cands = """
buffer buffer/push buffer/new buffer/blit buffer/format buffer/slice
string string/bytes string/from-bytes string/slice string/repeat string/join
table array tuple struct keyword symbol
type describe string/format printf pp print prin eprint eprintf
scan-number int? number? cmp compare
os/time os/clock os/cwd os/stat os/dir os/perm-string
math/random math/rng math/rng-int math/rng-buffer
gccollect gcsetinterval gcinterval trace-gc
buffer/push-string buffer/push-word buffer/push-byte
bxor band bor blshift brshift
inc dec
memcmp
array/concat array/push array/pop array/peek array/slice
pointer? abstract? cfunction?
""".split()

alive=[]
for c in cands:
    out=run(f"(print (type {c}))")
    line=out.strip().split(chr(10))[0]
    if 'unknown symbol' not in out and line and 'error' not in line:
        alive.append(c)
        print(f"ALIVE {c:24s} -> {line[:40]}")
    else:
        print(f"  --  {c:24s} -> {line[:40]}")
print()
print("ALIVE:", alive)
