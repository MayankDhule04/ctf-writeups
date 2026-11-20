import re
p=r"Temporal Paradox/gateway_snapshot.img"
b=open(p,"rb").read()
print("img size", len(b))
# find flag prefix, HTF, egress, base64 blobs, PEM, and 'R9' cipher markers, and any 'BEGIN'
for pat in [b"HTF{", b"egress", b"EGRESS", b"transfer", b"cipher", b"R9CF", b"C9TR", b"-----BEGIN", b"flag", b"nonce", b"key=", b"AES", b"chacha"]:
    i=0; hits=[]
    while True:
        j=b.find(pat,i)
        if j<0: break
        hits.append(j); i=j+1
        if len(hits)>8: break
    if hits: print(pat, "at", [hex(h) for h in hits])
# printable strings that look like base64 >= 40 chars
print("\n=== long base64-ish strings ===")
cnt=0
for m in re.finditer(rb"[A-Za-z0-9+/]{40,}={0,2}", b):
    s=m.group()
    print(hex(m.start()), len(s), s[:80].decode('latin1'))
    cnt+=1
    if cnt>20: break
