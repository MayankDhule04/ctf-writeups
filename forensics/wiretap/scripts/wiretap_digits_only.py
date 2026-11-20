#!/usr/bin/env python3
"""
Wiretap - Decode only the numeric digits
"""

full_seq = "AD1318A2016A3C141459521938A9A*4321539B1B17ABDA7265#5D09#8792568A14A1#92A4AB5#276C*D13*2D*40"

# Extract only digits
digits = ''.join(c for c in full_seq if c.isdigit())

print("="*70)
print("WIRETAP - DIGITS ONLY DECODE")
print("="*70)

print(f"\nFull sequence: {full_seq}")
print(f"Digits only: {digits}")
print(f"Length: {len(digits)}")

# Try as 2-digit ASCII codes
print(f"\n[1] As 2-digit ASCII codes:")
result = []
for i in range(0, len(digits)-1, 2):
    code = int(digits[i:i+2])
    char = chr(code) if 32 <= code <= 126 else '?'
    result.append(char)
    print(f"  {digits[i:i+2]} = {code:3d} = '{char}'")

text = ''.join(result)
print(f"\nDecoded: {text}")

if 'CIT{' in text:
    print(f"\n✓✓ FLAG FOUND: {text}")

# Try as 3-digit ASCII codes
print(f"\n[2] As 3-digit ASCII codes:")
result = []
for i in range(0, len(digits)-2, 3):
    code = int(digits[i:i+3])
    if 32 <= code <= 126:
        char = chr(code)
        result.append(char)
        print(f"  {digits[i:i+3]} = {code:3d} = '{char}'")

text = ''.join(result)
print(f"\nDecoded: {text}")

if 'CIT{' in text:
    print(f"\n✓✓ FLAG FOUND: {text}")

print(f"\n{'='*70}")
