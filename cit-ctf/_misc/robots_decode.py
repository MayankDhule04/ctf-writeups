#!/usr/bin/env python3
"""
Robots Challenge Decoder
Comment from robots.txt: q355q636678723p4

Possible encodings:
1. Hex to ASCII
2. Base conversion
3. Custom cipher
4. ROT13/Caesar
5. Leet speak reverse
"""

import base64
import binascii

comment = "q355q636678723p4"

print("="*70)
print("ROBOTS CHALLENGE - Decoding q355q636678723p4")
print("="*70)

# Try hex decode (if valid hex)
print("\n[*] Hex Decode Attempts:")
try:
    # Remove 'q' and try as hex
    hex_attempt = comment.replace('q', '').replace('p', '')
    decoded = bytes.fromhex(hex_attempt).decode('ascii', errors='ignore')
    print(f"    Without q/p: {decoded}")
except:
    pass

# Try treating q as 0, p as different values
print("\n[*] Substitution Attempts:")
substitutions = [
    ('q', '0'), ('q', '1'), ('q', '9'),
    ('p', '0'), ('p', '1'), ('p', '9'),
]
for old, new in substitutions:
    try:
        test = comment.replace(old, new)
        print(f"    {old}->{new}: {test}")
        # Try as hex
        try:
            decoded = bytes.fromhex(test).decode('ascii', errors='ignore')
            if decoded.isprintable():
                print(f"        -> Hex decode: {decoded}")
        except:
            pass
    except:
        pass

# Try base64 variations
print("\n[*] Base64 Attempts:")
for padding in ['', '=', '==', '===']:
    try:
        decoded = base64.b64decode(comment + padding).decode('ascii', errors='ignore')
        if decoded.isprintable():
            print(f"    With '{padding}': {decoded}")
    except:
        pass

# Try ROT13
print("\n[*] ROT13:")
rot13 = comment.translate(str.maketrans(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM'
))
print(f"    {rot13}")

# Try Caesar shifts
print("\n[*] Caesar Shifts (1-25):")
for shift in range(1, 26):
    result = ""
    for char in comment:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            result += char
    if shift <= 5 or shift >= 20:  # Show first/last few
        print(f"    Shift {shift:2d}: {result}")

# Try as coordinates or numbers
print("\n[*] Number Analysis:")
numbers = ''.join(c for c in comment if c.isdigit())
print(f"    Digits only: {numbers}")
print(f"    As ASCII codes: ", end="")
# Try pairs
for i in range(0, len(numbers)-1, 2):
    try:
        code = int(numbers[i:i+2])
        if 32 <= code <= 126:
            print(chr(code), end="")
    except:
        pass
print()

# Try triplets
print(f"    As ASCII (3-digit): ", end="")
for i in range(0, len(numbers)-2, 3):
    try:
        code = int(numbers[i:i+3])
        if 32 <= code <= 126:
            print(chr(code), end="")
    except:
        pass
print()

# Reverse
print("\n[*] Reversed:")
print(f"    {comment[::-1]}")

# Try as flag directly
print("\n[*] Direct Flag Attempts:")
flags = [
    f"CIT{{{comment}}}",
    f"CIT{{{comment.upper()}}}",
    f"CIT{{{comment.lower()}}}",
    f"CIT{{{''.join(c for c in comment if c.isalnum())}}}",
]
for flag in flags:
    print(f"    {flag}")

print("\n" + "="*70)
