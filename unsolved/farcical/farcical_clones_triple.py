#!/usr/bin/env python3
"""
Farcical Clones - Triple XOR or combined approach
Maybe we need to use all three ciphertexts together
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
cipher2 = [62, 150, 94, 172, 83, 135, 96, 153, 2, 208, 96, 172]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

print("="*70)
print("FARCICAL CLONES - TRIPLE XOR APPROACH")
print("="*70)

# Try: Flag XOR Cipher1 XOR Cipher2
print("[1] Flag XOR Cipher1 XOR Cipher2 (all repeating to match):")
result = []
for i in range(len(flag_nums)):
    val = flag_nums[i] ^ cipher1[i] ^ cipher2[i % len(cipher2)]
    result.append(val)

result_bytes = bytes(result)
print(f"  Result: {result_bytes}")
if all(32 <= b < 127 for b in result_bytes):
    print(f"  ✓ PRINTABLE: {result_bytes.decode('ascii')}")
    print(f"  ✓✓ FLAG: CIT{{{result_bytes.decode('ascii')}}}")

# Try: (Flag XOR Cipher1) XOR Cipher2
print("\n[2] (Flag XOR Cipher1) XOR Cipher2:")
xor1 = [flag_nums[i] ^ cipher1[i] for i in range(len(flag_nums))]
result = bytes([xor1[i] ^ cipher2[i % len(cipher2)] for i in range(len(xor1))])
print(f"  Result: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try: Flag XOR (Cipher1 XOR Cipher2)
print("\n[3] Flag XOR (Cipher1 XOR Cipher2):")
key = [cipher1[i] ^ cipher2[i % len(cipher2)] for i in range(len(cipher1))]
result = bytes([flag_nums[i] ^ key[i] for i in range(len(flag_nums))])
print(f"  Result: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Maybe cipher2 needs to be used twice?
print("\n[4] Flag XOR Cipher2 XOR Cipher2 (cancels out):")
result = bytes(flag_nums)  # Should be identity
print(f"  Result: {result} (identity, as expected)")

# What if we concatenate cipher1 and cipher2 as the key?
print("\n[5] Flag XOR (Cipher1 + Cipher2 concatenated):")
combined_key = cipher1 + cipher2
if len(combined_key) >= len(flag_nums):
    result = bytes([flag_nums[i] ^ combined_key[i] for i in range(len(flag_nums))])
    print(f"  Result: {result}")
    if all(32 <= b < 127 for b in result):
        print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# What if cipher1 and cipher2 are two parts of the same message?
print("\n[6] Cipher1 + Cipher2 as continuous ciphertext:")
combined_cipher = cipher1 + cipher2
print(f"  Combined length: {len(combined_cipher)}")

# Try XOR with a repeating key derived from the flag
print("\n[7] Using first 4 bytes of flag as key:")
key = flag_nums[:4]
result = bytes([flag_nums[i] ^ key[i % len(key)] for i in range(len(flag_nums))])
print(f"  Result: {result}")

# Try treating cipher2 as the actual key (not repeating, but as-is for first 12 bytes)
print("\n[8] Flag[:12] XOR Cipher2:")
result = bytes([flag_nums[i] ^ cipher2[i] for i in range(min(len(flag_nums), len(cipher2)))])
print(f"  Result: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# What if the hint "Farcical" means something? Farcical = absurd, ridiculous
# Maybe the cipher is intentionally silly/simple?
print("\n[9] Simple byte operations:")
# Try NOT operation
result = bytes([~n & 0xFF for n in flag_nums])
print(f"  NOT: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try XOR with 0xFF
result = bytes([n ^ 0xFF for n in flag_nums])
print(f"  XOR 0xFF: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try XOR with 0xAA (alternating bits)
result = bytes([n ^ 0xAA for n in flag_nums])
print(f"  XOR 0xAA: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

# Try XOR with 0x55
result = bytes([n ^ 0x55 for n in flag_nums])
print(f"  XOR 0x55: {result}")
if all(32 <= b < 127 for b in result):
    print(f"  ✓ PRINTABLE: {result.decode('ascii')}")

print("\n" + "="*70)
