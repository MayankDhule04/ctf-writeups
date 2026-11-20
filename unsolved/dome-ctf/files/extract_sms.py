import re, base64
f = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\MOBILE-EVIDENCE\MOBILE-EVIDENCE.img"
fh = open(f, "rb"); fh.seek(532833000); data = fh.read(4000); fh.close()

# find printable runs
runs = re.findall(rb"[ -~]{6,}", data)
for r in runs:
    s = r.decode("latin1")
    print(repr(s))

print("\n--- base64-looking tokens >=16 ---")
for r in runs:
    for tok in re.findall(rb"[A-Za-z0-9+/]{16,}={0,2}", r):
        t = tok.decode()
        print(t)
        try:
            dec = base64.b64decode(t + "===")
            print("   b64->", dec)
            # rot13
            rot = dec.decode('latin1')
            import codecs
            print("   rot13->", codecs.encode(rot, 'rot_13'))
        except Exception as e:
            print("   (not b64)", e)
