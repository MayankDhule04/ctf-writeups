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

tests = {
 "ffi/malloc":     "(print (type (ffi/malloc 16)))",
 "ffi/size":       "(print (ffi/size :int))",
 "ffi/align":      "(print (ffi/align :int))",
 "ffi/signature":  "(print (type (ffi/signature :default :void)))",
 "ffi/pointer-buffer":"(print (type (ffi/pointer-buffer (ffi/malloc 16) 16)))",
 "ffi/read":       "(print (ffi/read :int (ffi/malloc 16)))",
 "ffi/write":      "(print (type (ffi/write :int 5 (ffi/malloc 16))))",
 "ffi/jitfn":      "(print (type (ffi/jitfn (buffer/new 16))))",
 "ffi/lookup":     "(print (type (ffi/lookup)))",
 "ffi/trampoline": "(print (type (ffi/trampoline :default)))",
}
for name,form in tests.items():
    out=run(form)
    print(f"=== {name} ===")
    print("   ", out.strip().split(chr(10))[0][:80])
