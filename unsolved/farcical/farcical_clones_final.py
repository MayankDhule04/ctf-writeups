#!/usr/bin/env python3
"""
Farcical Clones - Try all combinations systematically
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
cipher2 = [62, 150, 94, 172, 83, 135, 96, 153, 2, 208, 96, 172]
cipher3_full = [201, 5, 19, 131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

print("="*70)
print("FARCICAL CLONES - SYSTEMATIC APPROACH")
print("="*70)

def xor_with_key(data, key):
    return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

def is_printable(data):
    return all(32 <= b < 127 for b in data)

# Try all combinations
tests = [
    ("Flag XOR Cipher1", flag_nums, cipher1),
    ("Flag XOR Cipher2 (repeating)", flag_nums, cipher2),
    ("Cipher1 XOR Cipher2 (repeating)", cipher1, cipher2),
    ("Cipher3 XOR Cipher1", cipher3_full[:len(cipher1)], cipher1),
    ("Cipher3 XOR Cipher2 (repeating)", cipher3_full, cipher2),
    ("Flag XOR Cipher1[:12]", flag_nums[:12], cipher1[:12]),
]

for name, data, key in tests:
    result = xor_with_key(data, key)
    print(f"\n[{name}]")
    print(f"  Result: {result}")
    if is_printable(result):
        print(f"  ✓ PRINTABLE: {result.decode('ascii')}")
        if result.decode('ascii').startswith('CIT{') or '}' in result.decode('ascii'):
            print(f"  ✓✓ LOOKS LIKE FLAG!")

# Try XOR with the prefix (201, 5, 19)
prefix = cipher3_full[:3]
print(f"\n[Flag XOR Prefix (repeating)]")
result = xor_with_key(flag_nums, prefix)
print(f"  Result: {result}")
if is_printable(result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try treating the numbers as already being XORed
# Maybe we need to XOR cipher1 and cipher2 together to get the key?
print(f"\n[Cipher1 XOR Cipher2 = Key, then Key XOR Flag]")
# First 12 bytes
key_candidate = xor_with_key(cipher1[:12], cipher2)
print(f"  Key candidate (12 bytes): {key_candidate}")

# Now use this key on the flag
result = xor_with_key(flag_nums, key_candidate)
print(f"  Flag XOR Key: {result}")
if is_printable(result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Maybe the structure is different - let's look at the raw data again
print(f"\n[Raw Analysis]")
print(f"  Cipher1 length: {len(cipher1)} bytes")
print(f"  Cipher2 length: {len(cipher2)} bytes")
print(f"  Flag length: {len(flag_nums)} bytes")
print(f"  Cipher3 full length: {len(cipher3_full)} bytes")
print(f"  Prefix: {cipher3_full[:3]}")

# What if cipher2 is the plaintext and cipher1 is key?
print(f"\n[Reverse: Cipher2 as plaintext]")
# Extend cipher2 to match cipher1 length
extended_cipher2 = (cipher2 * ((len(cipher1) // len(cipher2)) + 1))[:len(cipher1)]
result = xor_with_key(cipher1, extended_cipher2)
print(f"  Cipher1 XOR Cipher2(extended): {result}")
if is_printable(result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try simple operations
print(f"\n[Simple Operations on Flag]")
# Maybe it's ROT or Caesar
for shift in [13, 26, 32, 64, 128]:
    result = bytes([(n + shift) % 256 for n in flag_nums])
    if is_printable(result):
        print(f"  Add {shift}: {result.decode('ascii')}")
    
    result = bytes([(n - shift) % 256 for n in flag_nums])
    if is_printable(result):
        print(f"  Subtract {shift}: {result.decode('ascii')}")

print("\n" + "="*70)
