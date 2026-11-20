#!/usr/bin/env python3
"""
Robots Challenge - Comprehensive Analysis
String: q355q636678723p4

Looking for patterns:
- Leet speak (3=E, 5=S, 7=T, 0=O, 1=I, 4=A)
- Phone keypad encoding
- Custom substitution
"""

comment = "q355q636678723p4"

print("="*70)
print("ROBOTS CHALLENGE - Comprehensive Decoder")
print("="*70)

# Leet speak decode
print("\n[*] Leet Speak Decoding:")
leet_map = {
    '0': 'O', '1': 'I', '3': 'E', '4': 'A', '5': 'S',
    '7': 'T', '8': 'B', '9': 'g',
}

leet_decoded = ""
for char in comment:
    if char in leet_map:
        leet_decoded += leet_map[char]
    else:
        leet_decoded += char.upper()

print(f"    Standard leet: {leet_decoded}")
print(f"    Flag: CIT{{{leet_decoded}}}")

# Alternative leet mappings
alt_leet = {
    '0': 'O', '1': 'L', '3': 'E', '4': 'A', '5': 'S',
    '6': 'G', '7': 'T', '8': 'B', '9': 'g',
}
alt_decoded = ""
for char in comment:
    if char in alt_leet:
        alt_decoded += alt_leet[char]
    else:
        alt_decoded += char.upper()
print(f"    Alt leet (6=G): {alt_decoded}")
print(f"    Flag: CIT{{{alt_decoded}}}")

# Phone keypad (T9)
print("\n[*] Phone Keypad (T9) Decoding:")
# 2=ABC, 3=DEF, 4=GHI, 5=JKL, 6=MNO, 7=PQRS, 8=TUV, 9=WXYZ
phone_map = {
    '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
    '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ',
}
print(f"    Possible letters per digit:")
for char in comment:
    if char in phone_map:
        print(f"    {char} -> {phone_map[char]}")

# Try interpreting q and p as special markers
print("\n[*] Q and P as Markers:")
parts = comment.split('q')
print(f"    Split by 'q': {parts}")
parts = comment.split('p')
print(f"    Split by 'p': {parts}")

# Try hex with q=a, p=b
print("\n[*] Q=A, P=B Substitution:")
hex_attempt = comment.replace('q', 'a').replace('p', 'b')
print(f"    Substituted: {hex_attempt}")
try:
    decoded = bytes.fromhex(hex_attempt).decode('ascii', errors='ignore')
    print(f"    Hex decoded: {decoded}")
    print(f"    Flag: CIT{{{decoded}}}")
except Exception as e:
    print(f"    Not valid hex: {e}")

# Try q=c, p=d
hex_attempt2 = comment.replace('q', 'c').replace('p', 'd')
print(f"    Q=C, P=D: {hex_attempt2}")
try:
    decoded = bytes.fromhex(hex_attempt2).decode('ascii', errors='ignore')
    print(f"    Hex decoded: {decoded}")
    print(f"    Flag: CIT{{{decoded}}}")
except Exception as e:
    print(f"    Not valid hex")

# Binary interpretation
print("\n[*] Binary Patterns:")
# q=0, p=1
binary = comment.replace('q', '0').replace('p', '1')
print(f"    Q=0, P=1: {binary}")

# Try as octal
print("\n[*] Octal Interpretation:")
try:
    # Remove non-octal chars
    octal_str = ''.join(c for c in comment if c in '01234567')
    print(f"    Octal digits: {octal_str}")
    # Try groups of 3
    result = ""
    for i in range(0, len(octal_str), 3):
        if i+3 <= len(octal_str):
            code = int(octal_str[i:i+3], 8)
            if 32 <= code <= 126:
                result += chr(code)
    print(f"    Decoded: {result}")
    if result:
        print(f"    Flag: CIT{{{result}}}")
except Exception as e:
    print(f"    Error: {e}")

# Check if it's a hash or encoded value
print("\n[*] Hash/Encoding Check:")
print(f"    Length: {len(comment)}")
print(f"    Alphanumeric: {comment.isalnum()}")
print(f"    Could be MD5 (partial): {len(comment) == 16}")

# Try common CTF flag patterns
print("\n[*] Common Flag Patterns:")
patterns = [
    comment,
    comment.upper(),
    comment.lower(),
    comment.replace('q', 'Q').replace('p', 'P'),
    ''.join(c for c in comment if c.isdigit()),  # numbers only
    ''.join(c for c in comment if c.isalpha()),  # letters only
]
for p in patterns:
    print(f"    CIT{{{p}}}")

print("\n" + "="*70)
print("\n[!] Most likely candidates:")
print(f"    1. CIT{{{leet_decoded}}} (leet speak)")
print(f"    2. CIT{{{comment}}} (direct)")
print(f"    3. Check actual challenge page for more context")
print("="*70)
