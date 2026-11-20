#!/usr/bin/env python3
"""
Farcical Clones - Alternative interpretations
Maybe the numbers aren't direct byte values
"""

import string

cipher1_str = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094"
cipher2_str = "062 150 094 172 083 135 096 153 002 208 096 172"
flag_str = "131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238"

cipher1 = [int(x) for x in cipher1_str.split()]
cipher2 = [int(x) for x in cipher2_str.split()]
flag_nums = [int(x) for x in flag_str.split()]

print("="*70)
print("FARCICAL CLONES - ALTERNATIVE INTERPRETATIONS")
print("="*70)

# Maybe they're indices into an alphabet?
print("[1] As indices into alphabet (mod 26):")
alphabet = string.ascii_uppercase
result = ''.join(alphabet[n % 26] for n in flag_nums)
print(f"  Flag: {result}")
print(f"  With CIT: CIT{{{result.lower()}}}")

# Maybe they're indices into extended ASCII?
print("\n[2] As indices into printable ASCII (32-126):")
printable = string.printable[:95]  # ASCII 32-126
result = ''.join(printable[n % len(printable)] for n in flag_nums)
print(f"  Flag: {result}")

# Maybe modulo 256 then subtract something?
print("\n[3] Modulo operations:")
for mod in [64, 95, 128]:
    result = ''.join(chr((n % mod) + 32) if (n % mod) + 32 < 127 else '?' for n in flag_nums)
    print(f"  Mod {mod} + 32: {result}")

# Maybe they represent positions in a different encoding?
print("\n[4] As Base64 indices:")
b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
result = ''.join(b64_chars[n % 64] for n in flag_nums)
print(f"  Flag: {result}")

# Maybe subtract cipher1 from flag?
print("\n[5] Flag - Cipher1 (element-wise):")
result = [(flag_nums[i] - cipher1[i]) % 256 for i in range(len(flag_nums))]
print(f"  Result: {result}")
result_bytes = bytes(result)
if all(32 <= b < 127 for b in result_bytes):
    print(f"  ✓ PRINTABLE: {result_bytes.decode('ascii')}")

# Maybe add cipher1 and flag?
print("\n[6] Flag + Cipher1 (element-wise, mod 256):")
result = [(flag_nums[i] + cipher1[i]) % 256 for i in range(len(flag_nums))]
print(f"  Result: {result}")
result_bytes = bytes(result)
if all(32 <= b < 127 for b in result_bytes):
    print(f"  ✓ PRINTABLE: {result_bytes.decode('ascii')}")

# What if we need to decode cipher1 first, then use it as key?
print("\n[7] Trying to decode Cipher1 first:")
# Try XOR cipher1 with cipher2
decoded_cipher1 = bytes([cipher1[i] ^ cipher2[i % len(cipher2)] for i in range(len(cipher1))])
print(f"  Cipher1 XOR Cipher2: {decoded_cipher1}")
if all(32 <= b < 127 for b in decoded_cipher1):
    print(f"  ✓ Cipher1 decoded: {decoded_cipher1.decode('ascii')}")
    # Now use this as key for flag
    result = bytes([flag_nums[i] ^ decoded_cipher1[i] for i in range(len(flag_nums))])
    print(f"  Flag XOR decoded_cipher1: {result}")
    if all(32 <= b < 127 for b in result):
        print(f"  ✓✓ FLAG: {result.decode('ascii')}")

# Maybe the numbers are in a different base?
print("\n[8] Trying as hex (base 16) instead of decimal:")
try:
    # Interpret "095" as 0x95, etc.
    flag_hex = [int(str(n), 16) for n in flag_nums if int(str(n), 16) < 256]
    result = bytes(flag_hex)
    print(f"  As hex: {result}")
    if all(32 <= b < 127 for b in result):
        print(f"  ✓ PRINTABLE: {result.decode('ascii')}")
except:
    print(f"  (conversion error)")

# Try treating as octal (but we know 8 and 9 appear, so this will fail for some)
print("\n[9] Checking which numbers are valid octal:")
valid_octal = [n for n in flag_nums if all(d < '8' for d in str(n))]
print(f"  Valid octal numbers: {valid_octal}")
print(f"  Invalid (contain 8 or 9): {[n for n in flag_nums if n not in valid_octal]}")

# Maybe it's a polyalphabetic cipher where position matters?
print("\n[10] Vigenere-style with position:")
key = "FORCE"
result = []
for i, n in enumerate(flag_nums):
    shift = ord(key[i % len(key)]) - ord('A')
    # Try different interpretations
    val = (n - shift) % 256
    result.append(val)

result_bytes = bytes(result)
print(f"  With key 'FORCE': {result_bytes}")
if all(32 <= b < 127 for b in result_bytes):
    print(f"  ✓ PRINTABLE: {result_bytes.decode('ascii')}")

print("\n" + "="*70)
