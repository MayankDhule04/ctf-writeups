p=r"Temporal Paradox/gateway_snapshot.img"
b=open(p,"rb").read()

# 1) all HTF{ occurrences with context
print("=== HTF occurrences ===")
i=0; n=0
while True:
    j=b.find(b"HTF{", i)
    if j<0: break
    end=b.find(b"}", j)
    ctxs=b[max(0,j-60):j]
    print(hex(j), repr(b[j:end+1].decode('latin1','replace')), "| ctx:", repr(ctxs[-50:].decode('latin1','replace')))
    i=j+1; n+=1
    if n>40: break
print("total HTF:", n)

# 2) all R9CF blocks: parse header (magic, byte4, len@5-6)
print("\n=== R9CF blocks ===")
i=0
while True:
    j=b.find(b"R9CF", i)
    if j<0: break
    ln = b[j+5] | (b[j+6]<<8)
    lane=b[j+4]
    print(hex(j), "lane=",lane, "len=",ln, "raw=", b[j:j+min(ln,64)].hex())
    i=j+1
