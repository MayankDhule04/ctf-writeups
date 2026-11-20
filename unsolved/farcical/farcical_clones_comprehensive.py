#!/usr/bin/env python3
"""
Farcical Clones - Comprehensive Solver
Hint: "May the Force be with you, young padawan" + "Farcical Clones"
"""

cipher1 = "095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094"
cipher2 = "062 150 094 172 083 135 096 153 002 208 096 172"
cipher3 = "201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"

def parse_numbers(s):
    return [int(n) for n in s.replace('{', '').replace('}', '').split()]

nums1 = parse_numbers(cipher1)
nums2 = parse_numbers(cipher2)
nums3 = parse_numbers(cipher3)

# Extract just the flag content (inside braces)
flag_start = cipher3.index('{')
flag_end = cipher3.index('}')
flag_cipher = cipher3[flag_start+1:flag_end]
flag_nums = parse_numbers(flag_cipher)

print("="*70)
print("FARCICAL CLONES - COMPREHENSIVE SOLVER")
print("="*70)
print(f"Cipher 1 ({len(nums1)} bytes): {nums1}")
print(f"Cipher 2 ({len(nums2)} bytes): {nums2}")
print(f"Cipher 3 ({len(nums3)} bytes): {nums3}")
print(f"Flag part ({len(flag_nums)} bytes): {flag_nums}")
print()

# Try XOR with various keys
print("[1] XOR with multi-byte keys:")

keys_to_try = [
    b"FORCE",
    b"CLONE",
    b"CLONES",
    b"JEDI",
    b"SITH",
    b"YODA",
    b"PADAWAN",
    b"STARWARS",
    b"CIT",
    b"FLAG",
    b"KEY",
    b"BOOTSTRAP",
    b"999",
    # Try numbers
    bytes([66, 79, 79, 84]),  # BOOT
    bytes([0x42, 0x4F, 0x4F, 0x54]),  # BOOT in hex
]

def xor_with_key(numbers, key):
    result = []
    for i, n in enumerate(numbers):
        result.append(n ^ key[i % len(key)])
    return bytes(result)

for key in keys_to_try:
    try:
        decoded = xor_with_key(flag_nums, key)
        # Check if printable
        if all(32 <= b < 127 or b in [10, 13] for b in decoded):
            print(f"  Key {key}: {decoded}")
    except:
        pass

# Try all single-byte XOR keys
print("\n[2] Single-byte XOR on flag part:")
for key in range(256):
    decoded = bytes([n ^ key for n in flag_nums])
    if all(32 <= b < 127 for b in decoded):
        try:
            text = decoded.decode('ascii')
            if any(word in text.upper() for word in ['FLAG', 'CIT', 'THE', 'AND']):
                print(f"  Key {key} ('{chr(key) if 32 <= key < 127 else '?'}'): {text}")
        except:
            pass

# Try ROT cipher on the ASCII representation
print("\n[3] ROT cipher attempts:")
# First convert to ASCII
ascii_chars = ''.join(chr(n) if 32 <= n < 127 else '?' for n in flag_nums)
print(f"  ASCII representation: {ascii_chars}")

# Try different operations
print("\n[4] Mathematical operations:")

# Try subtracting a constant
for sub in [32, 64, 128, 200]:
    decoded = bytes([(n - sub) % 256 for n in flag_nums])
    if all(32 <= b < 127 for b in decoded):
        print(f"  Subtract {sub}: {decoded}")

# Try adding a constant
for add in [32, 64, 128]:
    decoded = bytes([(n + add) % 256 for n in flag_nums])
    if all(32 <= b < 127 for b in decoded):
        print(f"  Add {add}: {decoded}")

# Check if it's a simple substitution
print("\n[5] Analyzing patterns:")
print(f"  Unique values in flag: {len(set(flag_nums))}")
print(f"  Value range: {min(flag_nums)} - {max(flag_nums)}")
print(f"  Values: {sorted(set(flag_nums))}")

# Try XOR with the first three numbers (201 005 019) as a key
prefix_nums = nums3[:3]
print(f"\n[6] XOR with prefix {prefix_nums}:")
decoded = xor_with_key(flag_nums, bytes(prefix_nums))
print(f"  Result: {decoded}")
if all(32 <= b < 127 for b in decoded):
    print(f"  ASCII: {decoded.decode('ascii')}")

# Try XOR between cipher1 and cipher2 (they might be key material)
print(f"\n[7] Analyzing cipher relationships:")
print(f"  Cipher 1 length: {len(nums1)}")
print(f"  Cipher 2 length: {len(nums2)}")
print(f"  Flag length: {len(flag_nums)}")

# Maybe cipher1 or cipher2 is the key?
if len(nums1) == len(flag_nums):
    print(f"\n  Cipher1 length matches flag! Trying XOR:")
    decoded = bytes([flag_nums[i] ^ nums1[i] for i in range(len(flag_nums))])
    print(f"  Result: {decoded}")
    if all(32 <= b < 127 for b in decoded):
        print(f"  ASCII: {decoded.decode('ascii')}")

# Try using cipher2 as repeating key
print(f"\n[8] Using cipher2 as XOR key:")
decoded = xor_with_key(flag_nums, bytes(nums2))
print(f"  Result: {decoded}")
if all(32 <= b < 127 for b in decoded):
    print(f"  ASCII: {decoded.decode('ascii')}")

# Try using cipher1 as repeating key
print(f"\n[9] Using cipher1 as XOR key:")
decoded = xor_with_key(flag_nums, bytes(nums1))
print(f"  Result: {decoded}")
if all(32 <= b < 127 for b in decoded):
    print(f"  ASCII: {decoded.decode('ascii')}")

print("\n" + "="*70)
