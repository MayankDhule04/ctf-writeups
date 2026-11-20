#!/usr/bin/env python3
"""
Farcical Clones - Mathematical relationships
Check for arithmetic patterns
"""

cipher1 = [95, 181, 145, 39, 245, 91, 212, 232, 123, 220, 167, 69, 91, 208, 245, 164, 245, 145, 123, 94]
cipher2 = [62, 150, 94, 172, 83, 135, 96, 153, 2, 208, 96, 172]
flag_nums = [131, 91, 90, 53, 95, 218, 238, 211, 91, 4, 201, 182, 135, 245, 167, 74, 90, 145, 96, 238]

print("="*70)
print("FARCICAL CLONES - MATHEMATICAL ANALYSIS")
print("="*70)

# Check if flag = cipher1 + cipher2 (some combination)
print("[1] Checking: Flag = Cipher1 OP Cipher2")
for i in range(min(len(flag_nums), len(cipher1), len(cipher2))):
    f = flag_nums[i]
    c1 = cipher1[i]
    c2 = cipher2[i % len(cipher2)]
    
    print(f"Position {i:2d}: flag={f:3d}, c1={c1:3d}, c2={c2:3d}")
    print(f"  f-c1={f-c1:4d}, f-c2={f-c2:4d}, f+c1={f+c1:4d}, f+c2={f+c2:4d}")
    print(f"  f^c1={f^c1:4d}, f^c2={f^c2:4d}, c1^c2={c1^c2:4d}")
    print(f"  f=c1+c2? {f == c1+c2}, f=c1-c2? {f == c1-c2}, f=c1^c2? {f == c1^c2}")
    print()

# Check if there's a pattern in the differences
print("\n[2] Analyzing differences:")
diff_c1_flag = [flag_nums[i] - cipher1[i] for i in range(len(flag_nums))]
print(f"Flag - Cipher1: {diff_c1_flag}")

# Check if the difference is constant or follows a pattern
print(f"  Unique differences: {set(diff_c1_flag)}")
print(f"  Min: {min(diff_c1_flag)}, Max: {max(diff_c1_flag)}")

# Check modulo patterns
print("\n[3] Modulo patterns:")
for mod in [26, 64, 95, 128, 256]:
    result = [n % mod for n in flag_nums]
    print(f"  Flag mod {mod}: {result}")
    # Try to convert to ASCII
    if mod <= 95:
        chars = ''.join(chr((n % mod) + 32) if (n % mod) + 32 < 127 else '?' for n in flag_nums)
        print(f"    As ASCII (+32): {chars}")

# Check if cipher2 is the key pattern
print("\n[4] Using Cipher2 as a repeating pattern:")
# Maybe flag[i] = (cipher1[i] + cipher2[i%12]) % 256?
reconstructed = [(cipher1[i] + cipher2[i % len(cipher2)]) % 256 for i in range(len(cipher1))]
print(f"  Cipher1 + Cipher2 (mod 256): {reconstructed}")
print(f"  Matches flag? {reconstructed == flag_nums}")

# Try subtraction
reconstructed = [(cipher1[i] - cipher2[i % len(cipher2)]) % 256 for i in range(len(cipher1))]
print(f"  Cipher1 - Cipher2 (mod 256): {reconstructed}")
print(f"  Matches flag? {reconstructed == flag_nums}")

# Try XOR
reconstructed = [cipher1[i] ^ cipher2[i % len(cipher2)] for i in range(len(cipher1))]
print(f"  Cipher1 XOR Cipher2: {reconstructed}")
print(f"  Matches flag? {reconstructed == flag_nums}")

# What if we need to solve for the key?
# flag = cipher1 XOR key
# key = flag XOR cipher1
print("\n[5] Deriving the key:")
key = [flag_nums[i] ^ cipher1[i] for i in range(len(flag_nums))]
print(f"  Key (Flag XOR Cipher1): {key}")
print(f"  As bytes: {bytes(key)}")
print(f"  As ASCII: {bytes(key).decode('latin-1')}")

# Check if this key has a pattern
print(f"  Unique key bytes: {len(set(key))}")
print(f"  Key pattern: {set(key)}")

# Maybe the key is actually a message?
# Try XOR the key with cipher2
decoded_key = bytes([key[i] ^ cipher2[i % len(cipher2)] for i in range(len(key))])
print(f"\n  Key XOR Cipher2: {decoded_key}")
if all(32 <= b < 127 for b in decoded_key):
    print(f"  ✓ PRINTABLE: {decoded_key.decode('ascii')}")

print("\n" + "="*70)
