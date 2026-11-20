import base64
import requests
import json

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

# Get the flag data
r = requests.get(f"{BASE_URL}/api/flag", timeout=15)
flag_data = r.json()["flag"]

parts = flag_data.split("||")
print(f"Parts count: {len(parts)}")
print(f"Part lengths: {set(len(p) for p in parts)}")

# Decode each part as base32
all_decoded = []
for i, part in enumerate(parts):
    try:
        padded = part + "=" * ((8 - len(part) % 8) % 8)
        decoded = base64.b32decode(padded)
        all_decoded.append(decoded)
    except Exception as e:
        print(f"Part {i} error: {e}")
        all_decoded.append(b"")

# Print all decoded parts
print("\n=== All decoded parts (hex) ===")
for i, d in enumerate(all_decoded):
    print(f"Part {i:3d} ({len(d):2d} bytes): {d.hex()}")

# Check if each group of parts might form something
# Parts are 24 chars each (except maybe last), which is 15 bytes base32-decoded
# 125 parts * 15 bytes = 1875 bytes total

full_decoded = b"".join(all_decoded)
print(f"\nTotal decoded bytes: {len(full_decoded)}")
print(f"Full hex (first 200 bytes): {full_decoded[:200].hex()}")
print(f"Full text (first 200): {full_decoded[:200]}")

# Check if it's another encoding layer
# Try base64 decode of the decoded bytes
try:
    second_decode = base64.b64decode(full_decoded)
    print(f"\nBase64 layer 2: {second_decode[:200]}")
except:
    print("\nNot valid base64")

try:
    second_decode = base64.b32decode(full_decoded)
    print(f"\nBase32 layer 2: {second_decode[:200]}")
except:
    print("\nNot valid base32")

# Check for patterns - maybe every Nth byte
print("\n=== Pattern analysis ===")
for skip in [1, 2, 3, 4, 5, 10, 15]:
    chars = []
    for b in full_decoded[::skip]:
        if 32 <= b < 127:
            chars.append(chr(b))
        else:
            chars.append('.')
    text = ''.join(chars)
    if 'TRACE' in text or 'flag' in text.lower() or 'ctf' in text.lower():
        print(f"  Skip {skip}: FOUND MATCH: {text[:200]}")
    else:
        print(f"  Skip {skip}: {text[:100]}")

# Try XOR with common keys
print("\n=== XOR analysis ===")
for key_byte in range(256):
    result = bytes(b ^ key_byte for b in full_decoded)
    try:
        text = result.decode('ascii')
        if 'TRACE' in text or 'flag' in text.lower():
            print(f"  XOR key {key_byte}: {text[:200]}")
    except:
        pass

# Maybe each part decodes to a flag candidate and one is real
print("\n=== Individual part text ===")
for i, d in enumerate(all_decoded):
    try:
        text = d.decode('utf-8', errors='replace')
        if 'TRACE' in text or 'CTF' in text or 'flag' in text.lower():
            print(f"  Part {i}: {text}")
    except:
        pass

# Check if parts contain structured data (5 groups of 25?)
print(f"\n=== Part grouping analysis ===")
# 125 = 5 * 25 = 5^3
# Each part is some data. Maybe we need to pick correct parts

# Let's look at the raw base32 characters
print("\n=== Looking for flag in base32 chars ===")
# Maybe the || separators are the key - take specific characters
plain = flag_data.replace("||", "")
# Check if any substring looks like TRACECTF when base32 decoded
for i in range(0, len(plain) - 40, 8):
    chunk = plain[i:i+40]
    try:
        padded = chunk + "=" * ((8 - len(chunk) % 8) % 8)  
        d = base64.b32decode(padded)
        text = d.decode('ascii', errors='replace')
        if 'TRACE' in text:
            print(f"  Offset {i}: {text}")
    except:
        pass

# Take first char of each part
first_chars = "".join(p[0] for p in parts if p)
print(f"\nFirst char of each part: {first_chars}")
# Try base32 decoding that
try:
    padded = first_chars + "=" * ((8 - len(first_chars) % 8) % 8)
    d = base64.b32decode(padded)
    print(f"First chars decoded: {d}")
except Exception as e:
    print(f"First chars decode error: {e}")

# Take Nth char of each part
for n in range(24):
    chars = "".join(p[n] for p in parts if len(p) > n)
    try:
        padded = chars + "=" * ((8 - len(chars) % 8) % 8)
        d = base64.b32decode(padded)
        text = d.decode('utf-8', errors='replace')
        if any(c.isalpha() for c in text):
            print(f"Char position {n}: {text[:50]}")
    except:
        pass
