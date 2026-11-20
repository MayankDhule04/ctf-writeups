#!/usr/bin/env python3
from pwn import remote, context
import sys, time
context.log_level='error'
HOST="jailnet-5e659379e742.chall.nnsc.tf"; PORT=1337

def run(form, wait=2.0):
    io=remote(HOST,PORT,ssl=True)
    # wait for sandbox> prompt
    try:
        io.recvuntil(b'sandbox> ', timeout=8)
    except Exception:
        pass
    io.send(form.encode() if isinstance(form,str) else form)
    time.sleep(wait)
    data=b''
    t=time.time()
    while time.time()-t<wait+3:
        try:
            d=io.recv(timeout=2)
            if not d: break
            data+=d
        except Exception:
            break
    io.close()
    return data

if __name__=="__main__":
    form = sys.argv[1] if len(sys.argv)>1 else "(+ 1 2)"
    print("FORM:", form)
    out = run(form)
    print("OUT:", repr(out))
    try:
        print(out.decode(errors='replace'))
    except: pass
