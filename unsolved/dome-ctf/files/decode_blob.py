import base64, itertools

blob = "MT9gMF5wqTM7MKMcMTIhL2H6ZRA3HmyZFUOno3M3IJj5rIWOFxECL2y9"
key = b"vyrqelith"

def xor(data, k):
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))

# try base64 decode
try:
    raw = base64.b64decode(blob + "==")
    print("b64 len:", len(raw), raw.hex())
    print("b64 xor vyrqelith:", xor(raw, key))
except Exception as e:
    print("b64 fail", e)

# try urlsafe
try:
    raw2 = base64.urlsafe_b64decode(blob + "==")
    print("urlsafe xor:", xor(raw2, key))
except Exception as e:
    print("urlsafe fail", e)

# maybe the blob itself is ascii to be xored? no. 
# Try: treat as base64, xor with rot13(key)? and other keys
for k in [b"vyrqelith", b"nightlens_42", b"nightlens", b"iledryvgu", b"VYRQELITH"]:
    try:
        raw = base64.b64decode(blob + "==")
        out = xor(raw, k)
        printable = sum(1 for c in out if 32<=c<127)
        print(f"key={k.decode()}: printable={printable}/{len(out)} -> {out}")
    except Exception as e:
        print(k, "err", e)
