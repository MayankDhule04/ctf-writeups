#!/usr/bin/env python3
"""
Star Wars Force Challenge - SOLUTION
Mod 94 + 32 transformation looks promising!
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE - SOLUTION")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

import re
numbers = [int(n) for n in re.findall(r'\d+', message)]

print(f"\n📊 Total numbers: {len(numbers)}")

# The promising transformation: Mod 94 + 32
# This maps to printable ASCII range (32-125)
print("\n" + "=" * 70)
print("TRANSFORMATION: (n % 94) + 32")
print("=" * 70)

decoded_full = ""
for n in numbers:
    char_code = (n % 94) + 32
    decoded_full += chr(char_code)

print(f"\nFull decoded message:")
print(f"{decoded_full}")

# Extract the flag
flag_match = re.search(r'\{([^}]+)\}', decoded_full)
if flag_match:
    flag_content = flag_match.group(1)
    print(f"\n🏁 FLAG FOUND!")
    print(f"   Content: {flag_content}")
    print(f"   Full flag: {{{flag_content}}}")
    
    # Try common flag formats
    print(f"\n   Possible formats:")
    print(f"   CTF{{{flag_content}}}")
    print(f"   CIT{{{flag_content}}}")
    print(f"   FLAG{{{flag_content}}}")

# Also try other mod values that might work
print("\n" + "=" * 70)
print("TRYING OTHER MOD VALUES")
print("=" * 70)

for mod_val in [85, 90, 94, 95, 96, 100]:
    decoded = ""
    for n in numbers:
        char_code = (n % mod_val) + 32
        if 32 <= char_code <= 126:
            decoded += chr(char_code)
        else:
            decoded += '.'
    
    # Check if it looks readable
    readable = sum(1 for c in decoded if c.isalnum() or c in ' ,.!?{}') / len(decoded)
    if readable > 0.7:
        print(f"\nMod {mod_val} + 32: {decoded}")
        print(f"   Readable: {readable*100:.1f}%")
        
        # Extract flag if present
        flag_match = re.search(r'\{([^}]+)\}', decoded)
        if flag_match:
            print(f"   🏁 Flag: {{{flag_match.group(1)}}}")

# Try without the +32 offset
print("\n" + "=" * 70)
print("TRYING MOD WITHOUT +32 OFFSET")
print("=" * 70)

for mod_val in [94, 95, 96]:
    decoded = ""
    for n in numbers:
        char_code = n % mod_val
        if 32 <= char_code <= 126:
            decoded += chr(char_code)
        else:
            decoded += '.'
    
    readable = sum(1 for c in decoded if c.isalnum() or c in ' ,.!?{}') / len(decoded)
    if readable > 0.5:
        print(f"\nMod {mod_val}: {decoded}")
        flag_match = re.search(r'\{([^}]+)\}', decoded)
        if flag_match:
            print(f"   🏁 Flag: {{{flag_match.group(1)}}}")

print("\n" + "=" * 70)
print("SOLUTION COMPLETE")
print("=" * 70)
