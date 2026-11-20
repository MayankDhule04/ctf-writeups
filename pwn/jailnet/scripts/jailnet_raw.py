#!/usr/bin/env python3
from pwn import remote, context
import sys, time
context.log_level='error'
HOST="jailnet-5e659379e742.chall.nnsc.tf"; PORT=1337
form = sys.argv[1] if len(sys.argv)>1 else "(print (+ 1 2))"
io=remote(HOST,PORT,ssl=True)
time.sleep(1.5)
pre=b''
try: pre=io.recv(timeout=3)
except: pass
print("PRE-PROMPT:",repr(pre))
# send form terminated with newline
body = (form + "\n").encode()
# pad to exactly 4096 bytes so (file/read stdin 4096) returns immediately
if len(body) < 4096:
    body = body + b" " * (4096 - len(body))
io.send(body)
time.sleep(4)
data=b''
t=time.time()
while time.time()-t<8:
    try:
        d=io.recv(timeout=2)
        if not d: break
        data+=d
    except: break
print("AFTER:",repr(data))
try: print(data.decode(errors='replace'))
except: pass
io.close()
