#!/usr/bin/env python3
from pwn import remote, context
import time
context.log_level='info'
HOST="coins-a265f2d26226.chall.nnsc.tf"; PORT=1337
io=remote(HOST,PORT,ssl=True)
time.sleep(1.5)
try:
    data=io.recv(timeout=5)
except Exception:
    data=b''
print("=== initial output ===")
print(repr(data))
print()
print(data.decode(errors='ignore'))
io.close()
