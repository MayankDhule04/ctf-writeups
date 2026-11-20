import re
p=r"Temporal Paradox/gateway_snapshot.img"
b=open(p,"rb").read()
print("img size", len(b))

# 1) All ELF headers
elfs=[m.start() for m in re.finditer(rb'\x7fELF', b)]
print("ELF headers:", [hex(x) for x in elfs])

# 2) All ext4-visible filenames? just scan for interesting keywords
for kw in [b'r9sampler', b'deltaforge', b'egress', b'keystream', b'AES', b'decoder',
           b'encoder', b'mirror', b'flag', b'FLAG', b'HTF', b'.py', b'python',
           b'#!/', b'PK\x03\x04', b'GZIP', b'\x1f\x8b', b'sqlite', b'gateway']:
    hits=[m.start() for m in re.finditer(re.escape(kw), b)]
    if hits:
        print(kw, len(hits), [hex(x) for x in hits[:8]])
