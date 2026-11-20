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

ffi_syms=["ffi/native","ffi/lookup","ffi/signature","ffi/call","ffi/read",
          "ffi/write","ffi/malloc","ffi/free","ffi/pointer-buffer","ffi/buffer",
          "ffi/size","ffi/align","ffi/jitfn","ffi/trampoline","ffi/pointer-cfunction"]
for s in ffi_syms:
    out=run(f"(print (type {s}))")
    print(f"{s:26s} -> {out.strip().split(chr(10))[0][:50]}")
