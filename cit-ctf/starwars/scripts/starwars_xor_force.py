#!/usr/bin/env python3
"""
Star Wars Force Challenge - XOR with "Force" key
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE - XOR DECODER")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

import re
numbers = [int(n) for n in re.findall(r'\d+', message)]

print(f"\n📊 {len(numbers)} decimal numbers (range: {min(numbers)}-{max(numbers)})")

# Try XOR with various Star Wars related keys
keys = [
    "FORCE",
    "Force",
    "force",
    "YODA",
    "Yoda",
    "yoda",
    "JEDI",
    "Jedi",
    "jedi",
    "STAR",
    "Star",
    "star",
    "WARS",
    "Wars",
    "wars",
    "LUKE",
    "Luke",
    "luke",
    "VADER",
    "Vader",
    "vader",
    "PADAWAN",
    "Padawan",
    "padawan",
    "SKYWALKER",
    "Skywalker",
    "skywalker",
    "May the Force be with you",
    "MaytheForce",
    "TheForce",
]

print("\n" + "=" * 70)
print("XOR DECODING WITH STAR WARS KEYS")
print("=" * 70)

for key_str in keys:
    key_bytes = [ord(c) for c in key_str]
    decoded = ""
    
    for i, n in enumerate(numbers):
        if n > 255:
            decoded += '?'
            continue
        xor_val = n ^ key_bytes[i % len(key_bytes)]
        if 32 <= xor_val <= 126:
            decoded += chr(xor_val)
        elif xor_val in [10, 13]:  # newline
            decoded += ' '
        else:
            decoded += '.'
    
    # Check readability
    readable_chars = sum(1 for c in decoded if c not in '.?')
    readable_ratio = readable_chars / len(decoded)
    
    if readable_ratio > 0.7:  # At least 70% readable
        print(f"\n🔑 Key: '{key_str}'")
        print(f"   Decoded: {decoded}")
        print(f"   Readable: {readable_ratio*100:.1f}%")
        
        # Extract flag if present
        flag_match = re.search(r'\{([^}]+)\}', decoded)
        if flag_match:
            print(f"   🏁 Flag: {{{flag_match.group(1)}}}")

# Also try single-byte XOR exhaustively
print("\n" + "=" * 70)
print("EXHAUSTIVE SINGLE-BYTE XOR")
print("=" * 70)

best_results = []

for key in range(256):
    decoded = ""
    for n in numbers:
        if n > 255:
            decoded += '?'
            continue
        xor_val = n ^ key
        if 32 <= xor_val <= 126:
            decoded += chr(xor_val)
        else:
            decoded += '.'
    
    readable_chars = sum(1 for c in decoded if c != '.' and c != '?')
    readable_ratio = readable_chars / len(decoded)
    
    if readable_ratio > 0.7:
        best_results.append((key, decoded, readable_ratio))

# Sort by readability
best_results.sort(key=lambda x: x[2], reverse=True)

print(f"\nFound {len(best_results)} promising results:")
for key, decoded, ratio in best_results[:10]:  # Top 10
    key_char = chr(key) if 32 <= key <= 126 else f"0x{key:02x}"
    print(f"\n🔑 Key: {key} ('{key_char}')")
    print(f"   Decoded: {decoded}")
    print(f"   Readable: {ratio*100:.1f}%")

print("\n" + "=" * 70)
