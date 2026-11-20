import base64, hashlib, string, codecs

blob_b64 = "MT9gMF5wqTM7MKMcMTIhL2H6ZRA3HmyZFUOno3M3IJj5rIWOFxECL2y9"
raw = base64.b64decode(blob_b64 + "===")
print("raw len", len(raw), raw.hex())

keys = [b"vyrqelith", b"iledryvgu", b"nightlens_42", b"nightlens",
        b"Max42", b"max42", b"nightlens_42", b"VYRQELITH",
        b"CorrectHorseBatteryStaple", b"Welcome2026!",
        b"vyrqelith_42", b"nightlens42"]

def printable_score(b):
    return sum(1 for c in b if 32 <= c < 127 or c in (9,10,13))

def xor(data, k):
    return bytes(c ^ k[i % len(k)] for i, c in enumerate(data))

print("\n=== repeating-key XOR ===")
best = []
for k in keys:
    out = xor(raw, k)
    sc = printable_score(out)
    best.append((sc, k, out))
best.sort(reverse=True, key=lambda x: x[0])
for sc, k, out in best[:6]:
    print(f"{sc:3d}/{len(raw)} key={k.decode(errors='replace'):28s} {out}")

# AES attempts
try:
    from Crypto.Cipher import AES
    have_aes = True
except Exception:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        have_aes = 'cryptography'
    except Exception:
        have_aes = False
print("\n=== AES available:", have_aes, "===")

def try_aes(ct, key):
    results = []
    if len(ct) % 16 == 0:
        try:
            from Crypto.Cipher import AES
            for mode_name, c in [("ECB", AES.new(key, AES.MODE_ECB))]:
                try:
                    results.append((mode_name, c.decrypt(ct)))
                except Exception: pass
        except Exception: pass
    # GCM: last 16 bytes tag
    return results

if have_aes:
    for k in keys:
        key16 = hashlib.md5(k).digest()
        key32 = hashlib.sha256(k).digest()
        for key in (key16, key32):
            for name, out in try_aes(raw, key):
                if printable_score(out) > len(out)*0.7:
                    print(f"AES-{name} key_from={k} -> {out}")

# Vigenere on the base64 text itself (letters) with key
print("\n=== Vigenere on b64 text ===")
def vig_dec(text, key):
    res = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = key[ki % len(key)].lower()
            res.append(chr((ord(ch) - base - (ord(k)-97)) % 26 + base))
            ki += 1
        else:
            res.append(ch)
    return "".join(res)

for k in ["vyrqelith","nightlens","max42"]:
    v = vig_dec(blob_b64, k)
    print(k, "->", v)
    try:
        d = base64.b64decode(v + "===")
        if printable_score(d) > len(d)*0.8:
            print("   decoded:", d)
    except Exception: pass
