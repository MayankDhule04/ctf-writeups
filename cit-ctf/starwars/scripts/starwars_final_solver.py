#!/usr/bin/env python3
"""
Star Wars Force Challenge - Final Comprehensive Solver
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE - COMPREHENSIVE SOLVER")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

import re
numbers = [int(n) for n in re.findall(r'\d+', message)]

print(f"\n📊 Numbers: {numbers[:10]}... ({len(numbers)} total)")
print(f"   Range: {min(numbers)}-{max(numbers)}")

# Try treating as octal STRING (not octal numbers)
print("\n" + "=" * 70)
print("APPROACH 1: Treat as Octal Digits in Decimal")
print("=" * 70)

# Each 3-digit group might represent an octal character
octal_groups = re.findall(r'\d{3}', message.replace(' ', ''))
print(f"Found {len(octal_groups)} 3-digit groups")

decoded = ""
for group in octal_groups[:20]:  # First 20
    try:
        # Treat the decimal number as if it were octal
        octal_val = int(group, 8)
        if 32 <= octal_val <= 126:
            decoded += chr(octal_val)
        else:
            decoded += '.'
    except:
        decoded += '?'

print(f"Decoded: {decoded}")

# Try binary representation
print("\n" + "=" * 70)
print("APPROACH 2: Binary Analysis")
print("=" * 70)

# Convert to binary and look for patterns
binary_str = ''.join(f"{n:08b}" for n in numbers[:10])
print(f"First 10 numbers as binary: {binary_str}")

# Try 7-bit chunks
decoded_7bit = ""
for i in range(0, len(binary_str) - 6, 7):
    chunk = binary_str[i:i+7]
    val = int(chunk, 2)
    if 32 <= val <= 126:
        decoded_7bit += chr(val)
    else:
        decoded_7bit += '.'

print(f"7-bit chunks: {decoded_7bit}")

# Try ROT cipher
print("\n" + "=" * 70)
print("APPROACH 3: ROT Cipher on Numbers")
print("=" * 70)

for rot in [13, 47, 128]:
    decoded = ""
    for n in numbers:
        rotated = (n + rot) % 256
        if 32 <= rotated <= 126:
            decoded += chr(rotated)
        else:
            decoded += '.'
    
    readable = sum(1 for c in decoded if c != '.') / len(decoded)
    if readable > 0.5:
        print(f"ROT{rot}: {decoded} ({readable*100:.1f}% readable)")

# Try as coordinates or pairs
print("\n" + "=" * 70)
print("APPROACH 4: Pairs/Coordinates")
print("=" * 70)

# Take pairs of numbers
pairs = [(numbers[i], numbers[i+1]) for i in range(0, len(numbers)-1, 2)]
print(f"First 5 pairs: {pairs[:5]}")

# Try XOR of pairs
decoded_pairs = ""
for a, b in pairs:
    xor_val = a ^ b
    if 32 <= xor_val <= 126:
        decoded_pairs += chr(xor_val)
    else:
        decoded_pairs += '.'

print(f"XOR of pairs: {decoded_pairs}")

# Try sum of pairs mod 256
decoded_sum = ""
for a, b in pairs:
    sum_val = (a + b) % 256
    if 32 <= sum_val <= 126:
        decoded_sum += chr(sum_val)
    else:
        decoded_sum += '.'

print(f"Sum of pairs: {decoded_sum}")

# Focus on the flag section
print("\n" + "=" * 70)
print("APPROACH 5: Flag Section Deep Dive")
print("=" * 70)

flag_match = re.search(r'\{([^}]+)\}', message)
if flag_match:
    flag_numbers = [int(n) for n in re.findall(r'\d+', flag_match.group(1))]
    print(f"\nFlag numbers: {flag_numbers}")
    print(f"Length: {len(flag_numbers)}")
    
    # Try all transformations on flag
    print("\nTransformations:")
    
    # Direct
    print(f"  Direct: {''.join(chr(n) if 32 <= n <= 126 else '.' for n in flag_numbers)}")
    
    # Mod operations
    for mod in [128, 94, 85]:
        decoded = ''.join(chr(n % mod + 32) if n % mod + 32 <= 126 else '.' for n in flag_numbers)
        print(f"  Mod {mod} + 32: {decoded}")
    
    # XOR with first number
    if flag_numbers:
        key = flag_numbers[0]
        decoded = ''.join(chr(n ^ key) if 32 <= (n ^ key) <= 126 else '.' for n in flag_numbers)
        print(f"  XOR with first ({key}): {decoded}")
    
    # Subtract first number
    if flag_numbers:
        key = flag_numbers[0]
        decoded = ''.join(chr(n - key + 32) if 32 <= (n - key + 32) <= 126 else '.' for n in flag_numbers)
        print(f"  Subtract first + 32: {decoded}")

# Try interpreting as different bases
print("\n" + "=" * 70)
print("APPROACH 6: Different Base Interpretations")
print("=" * 70)

# Maybe they're hex values in decimal?
hex_attempt = ''.join(f"{n:02x}" for n in numbers[:20])
print(f"As hex string: {hex_attempt}")

try:
    decoded_hex = bytes.fromhex(hex_attempt).decode('utf-8', errors='ignore')
    print(f"Decoded from hex: {decoded_hex}")
except:
    print("Not valid hex")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
