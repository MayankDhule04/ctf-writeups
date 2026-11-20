#!/usr/bin/env python3
from pwn import remote, context
import time, re
context.log_level='error'
HOST="coins-a265f2d26226.chall.nnsc.tf"; PORT=1337
io=remote(HOST,PORT,ssl=True)
buf=b''
t=time.time()
while time.time()-t < 6:
    try:
        d=io.recv(timeout=2)
        if d: buf+=d
    except Exception:
        break
    if b'\n' in buf and buf.count(b'\n')>=3:
        break
print("=== full initial output ===")
print(repr(buf))
print()
print(buf.decode(errors='ignore'))
io.close()
