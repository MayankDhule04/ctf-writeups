import base64
import requests

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

r = requests.get(f"{BASE_URL}/api/flag", timeout=15)
flag_data = r.json()["flag"]

parts = flag_data.split("||")

# Decode each part
all_decoded = []
for part in parts:
    padded = part + "=" * ((8 - len(part) % 8) % 8)
    decoded = base64.b32decode(padded)
    all_decoded.append(decoded)

full = b"".join(all_decoded)
text = full.decode('ascii', errors='replace')
print(f"Full decoded text:\n{text}\n")

# Split by :: 
segments = text.split("::")
print(f"\nSegments count: {len(segments)}")
for i, seg in enumerate(segments):
    print(f"Seg {i:3d} ({len(seg):2d} chars): {repr(seg)}")

# Maybe this is a scrambled/encoded flag
# Each segment looks like random printable ASCII
# Let's see if there's a pattern

# Check if taking specific characters from each segment gives the flag
print("\n=== Taking chars at positions from segments ===")
for pos in range(max(len(s) for s in segments if s)):
    chars = []
    for s in segments:
        if len(s) > pos:
            chars.append(s[pos])
    result = ''.join(chars)
    if 'TRACE' in result:
        print(f"Pos {pos}: *** {result}")
    else:
        print(f"Pos {pos}: {result[:80]}")

# Try XOR between adjacent segments
print("\n=== XOR adjacent segments ===")
for i in range(len(segments) - 1):
    if len(segments[i]) == len(segments[i+1]):
        xored = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(segments[i], segments[i+1]))
        printable = ''.join(c if 32 <= ord(c) < 127 else '.' for c in xored)
        if 'TRACE' in printable or 'CTF' in printable:
            print(f"  {i}^{i+1}: {printable}")

# Maybe it's a cipher text and we should look for the flag differently
# Let's check: are these segments all the same length?
print(f"\nSegment lengths: {[len(s) for s in segments]}")
