#!/usr/bin/env python3
"""
Star Wars - Try Alternative Cipher Types
"""

import re

print("=" * 70)
print("STAR WARS - ALTERNATIVE CIPHER APPROACHES")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

numbers = [int(n) for n in re.findall(r'\d+', message)]

print(f"\n📊 {len(numbers)} numbers")

# Approach 1: Maybe they're indices into an alphabet
print("\n" + "=" * 70)
print("APPROACH 1: Numbers as Alphabet Indices")
print("=" * 70)

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
extended_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?{}"

for alpha in [alphabet, extended_alphabet]:
    decoded = ""
    for n in numbers:
        if n < len(alpha):
            decoded += alpha[n]
        else:
            decoded += '?'
    
    print(f"\nAlphabet ({len(alpha)} chars): {decoded[:80]}...")

# Approach 2: Affine cipher (ax + b) mod 256
print("\n" + "=" * 70)
print("APPROACH 2: Affine Cipher")
print("=" * 70)

print("Testing affine transformations...")

best_affine = []

for a in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]:  # Coprime with 256
    for b in range(0, 256, 10):  # Sample b values
        decoded = ""
        valid = True
        for n in numbers:
            val = (a * n + b) % 256
            if 32 <= val <= 126:
                decoded += chr(val)
            else:
                decoded += '.'
        
        readable = sum(1 for c in decoded if c != '.') / len(decoded)
        if readable > 0.7:
            best_affine.append((a, b, decoded, readable))

best_affine.sort(key=lambda x: x[3], reverse=True)

print(f"Found {len(best_affine)} promising affine transformations:")
for a, b, decoded, ratio in best_affine[:5]:
    print(f"\n   a={a}, b={b}: {decoded[:80]}... ({ratio*100:.1f}%)")

# Approach 3: Maybe it's base64 encoded numbers?
print("\n" + "=" * 70)
print("APPROACH 3: Numbers as Base64 Indices")
print("=" * 70)

base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

decoded = ""
for n in numbers:
    if n < len(base64_chars):
        decoded += base64_chars[n]
    else:
        decoded += '?'

print(f"Base64 string: {decoded}")

# Try to decode it
import base64
try:
    # Remove any ? characters
    clean = decoded.replace('?', '')
    # Pad if necessary
    while len(clean) % 4 != 0:
        clean += '='
    
    decoded_bytes = base64.b64decode(clean, validate=False)
    decoded_text = decoded_bytes.decode('utf-8', errors='ignore')
    print(f"Decoded from base64: {decoded_text}")
except Exception as e:
    print(f"Base64 decode failed: {e}")

# Approach 4: Vigenère cipher with numeric key
print("\n" + "=" * 70)
print("APPROACH 4: Vigenère-style with Numeric Key")
print("=" * 70)

# Try using first few numbers as the key
for key_len in [2, 3, 4, 5, 6, 7, 8]:
    key = numbers[:key_len]
    decoded = ""
    
    for i, n in enumerate(numbers):
        # Subtract the key value
        val = (n - key[i % key_len]) % 256
        if 32 <= val <= 126:
            decoded += chr(val)
        else:
            decoded += '.'
    
    readable = sum(1 for c in decoded if c != '.') / len(decoded)
    if readable > 0.5:
        print(f"\nKey length {key_len}, key={key}: {decoded[:80]}... ({readable*100:.1f}%)")

# Approach 5: Maybe numbers represent pairs (x,y coordinates)?
print("\n" + "=" * 70)
print("APPROACH 5: Pairs as Coordinates")
print("=" * 70)

# Split into pairs
pairs = [(numbers[i], numbers[i+1]) for i in range(0, len(numbers)-1, 2)]
print(f"First 5 pairs: {pairs[:5]}")

# Try different operations on pairs
operations = [
    ("XOR", lambda a, b: a ^ b),
    ("ADD mod 256", lambda a, b: (a + b) % 256),
    ("SUB mod 256", lambda a, b: (a - b) % 256),
    ("MUL mod 256", lambda a, b: (a * b) % 256),
    ("AVG", lambda a, b: (a + b) // 2),
]

for op_name, op_func in operations:
    decoded = ""
    for a, b in pairs:
        val = op_func(a, b)
        if 32 <= val <= 126:
            decoded += chr(val)
        else:
            decoded += '.'
    
    readable = sum(1 for c in decoded if c != '.') / len(decoded)
    if readable > 0.5:
        print(f"\n{op_name}: {decoded} ({readable*100:.1f}%)")

# Approach 6: ROT on the numbers themselves
print("\n" + "=" * 70)
print("APPROACH 6: ROT Cipher on Numbers")
print("=" * 70)

for rot in [13, 26, 47, 64, 128, 200]:
    decoded = ""
    for n in numbers:
        val = (n + rot) % 256
        if 32 <= val <= 126:
            decoded += chr(val)
        else:
            decoded += '.'
    
    readable = sum(1 for c in decoded if c != '.') / len(decoded)
    if readable > 0.5:
        print(f"\nROT{rot}: {decoded[:80]}... ({readable*100:.1f}%)")

# Approach 7: Maybe it's a simple substitution based on position
print("\n" + "=" * 70)
print("APPROACH 7: Position-based Transformation")
print("=" * 70)

# Subtract position from value
decoded = ""
for i, n in enumerate(numbers):
    val = (n - i) % 256
    if 32 <= val <= 126:
        decoded += chr(val)
    else:
        decoded += '.'

readable = sum(1 for c in decoded if c != '.') / len(decoded)
print(f"Subtract position: {decoded[:80]}... ({readable*100:.1f}%)")

# Add position
decoded = ""
for i, n in enumerate(numbers):
    val = (n + i) % 256
    if 32 <= val <= 126:
        decoded += chr(val)
    else:
        decoded += '.'

readable = sum(1 for c in decoded if c != '.') / len(decoded)
print(f"Add position: {decoded[:80]}... ({readable*100:.1f}%)")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
