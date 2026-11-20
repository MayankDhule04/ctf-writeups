#!/usr/bin/env python3
"""
Star Wars Force Challenge - Advanced Solver
Try multiple decoding strategies
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE - ADVANCED SOLVER")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

# Parse all numbers
import re
numbers = [int(n, 8) for n in re.findall(r'\d+', message)]

print(f"\n📊 Parsed {len(numbers)} octal numbers")
print(f"   Range: {min(numbers)} to {max(numbers)}")

# Strategy 1: Modulo 128 (7-bit ASCII)
print("\n" + "=" * 70)
print("STRATEGY 1: Modulo 128 (7-bit ASCII)")
print("=" * 70)

decoded = ''.join(chr(n % 128) for n in numbers)
print(f"Decoded: {decoded}")

# Strategy 2: Modulo 256 (8-bit)
print("\n" + "=" * 70)
print("STRATEGY 2: Modulo 256 (8-bit)")
print("=" * 70)

decoded = ''.join(chr(n % 256) for n in numbers)
print(f"Decoded: {decoded}")

# Strategy 3: XOR with repeating key
print("\n" + "=" * 70)
print("STRATEGY 3: XOR with Repeating Keys")
print("=" * 70)

# Try "FORCE", "YODA", "JEDI", "STAR"
keys = ["FORCE", "YODA", "JEDI", "STAR", "WARS", "LUKE", "VADER"]

for key_str in keys:
    key_bytes = [ord(c) for c in key_str]
    decoded = ""
    for i, n in enumerate(numbers):
        byte_val = n % 256
        xor_val = byte_val ^ key_bytes[i % len(key_bytes)]
        if 32 <= xor_val <= 126:
            decoded += chr(xor_val)
        else:
            decoded += '.'
    
    # Check if it looks readable
    readable_ratio = sum(1 for c in decoded if c != '.') / len(decoded)
    if readable_ratio > 0.5:
        print(f"\nKey '{key_str}': {decoded}")
        print(f"   Readable: {readable_ratio*100:.1f}%")

# Strategy 4: Subtract offset
print("\n" + "=" * 70)
print("STRATEGY 4: Subtract Common Offsets")
print("=" * 70)

offsets = [128, 64, 32, 100, 200]
for offset in offsets:
    decoded = ""
    valid = True
    for n in numbers:
        adjusted = n - offset
        if 32 <= adjusted <= 126:
            decoded += chr(adjusted)
        else:
            valid = False
            break
    
    if valid:
        print(f"\nOffset -{offset}: {decoded}")

# Strategy 5: Look at the structure
print("\n" + "=" * 70)
print("STRATEGY 5: Analyze Structure")
print("=" * 70)

# Split by the delimiters in original
parts = message.split(',')
print(f"\nPart 1 (before comma): {parts[0]}")
if len(parts) > 1:
    part2_split = parts[1].split('.')
    print(f"Part 2 (after comma, before period): {part2_split[0]}")
    if len(part2_split) > 1:
        print(f"Part 3 (after period): {part2_split[1]}")

# Extract just the flag part
flag_match = re.search(r'\{([^}]+)\}', message)
if flag_match:
    flag_octals = [int(n, 8) for n in re.findall(r'\d+', flag_match.group(1))]
    print(f"\n🏁 Flag section has {len(flag_octals)} numbers")
    
    # Try different decodings for flag
    print("\nFlag attempts:")
    
    # Mod 128
    flag_decoded = ''.join(chr(n % 128) for n in flag_octals)
    print(f"   Mod 128: {flag_decoded}")
    
    # Mod 256
    flag_decoded = ''.join(chr(n % 256) for n in flag_octals)
    print(f"   Mod 256: {flag_decoded}")
    
    # Subtract 64
    try:
        flag_decoded = ''.join(chr(n - 64) for n in flag_octals if 64 <= n <= 190)
        print(f"   Minus 64: {flag_decoded}")
    except:
        pass

# Strategy 6: Maybe it's base-8 representation of hex?
print("\n" + "=" * 70)
print("STRATEGY 6: Octal as Hex Digits")
print("=" * 70)

# Treat octal numbers as hex
hex_str = ''.join(f"{n:02x}" for n in numbers)
print(f"Hex string: {hex_str[:100]}...")

# Try to decode as hex
try:
    decoded = bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
    print(f"Decoded: {decoded}")
except:
    print("Not valid hex encoding")

print("\n" + "=" * 70)
