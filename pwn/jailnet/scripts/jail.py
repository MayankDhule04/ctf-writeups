#!/usr/bin/env python3
from pwn import remote, context
import sys, time
context.log_level='error'
HOST="jailnet-4155a79b5812.chall.nnsc.tf"; PORT=1337

def run(form, wait=3.0):
    io=remote(HOST,PORT,ssl=True)
    time.sleep(0.8)
    try: io.recvuntil(b'sandbox> ', timeout=6)
    except: pass
    body=(form+"\n").encode()
    if len(body)<4096: body+=b" "*(4096-len(body))
    io.send(body)
    time.sleep(wait)
    data=b''
    t=time.time()
    while time.time()-t<wait+3:
        try:
            d=io.recv(timeout=2)
            if not d: break
            data+=d
        except: break
    io.close()
    return data

if __name__=="__main__":
    if sys.argv[1]=="-f":
        form=open(sys.argv[2],"r",encoding="utf-8").read()
    else:
        form=sys.argv[1]
    out=run(form)
    print(out.decode(errors='replace'))
