#!/usr/bin/env python3
"""
Star Wars Force Challenge Solver
"May the Force be with you, young padawan."
Octal encoded message
"""

print("=" * 70)
print("STAR WARS FORCE CHALLENGE SOLVER")
print("=" * 70)

# The octal encoded message
message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

print(f"\n🔍 Original message:")
print(f"   {message}")

# Parse octal numbers
octal_numbers = message.replace(',', '').replace('.', '').replace('{', '').replace('}', '').split()

print(f"\n📊 Found {len(octal_numbers)} octal numbers")

# Method 1: Direct octal to ASCII
print("\n" + "=" * 70)
print("METHOD 1: Direct Octal to ASCII")
print("=" * 70)

decoded = ""
for octal in octal_numbers:
    try:
        # Convert octal to decimal, then to character
        decimal = int(octal, 8)
        if 0 <= decimal <= 127:  # Valid ASCII range
            decoded += chr(decimal)
        else:
            decoded += f"[{decimal}]"
    except:
        decoded += f"[?{octal}]"

print(f"\nDecoded: {decoded}")

# Method 2: Preserve structure (commas, periods, braces)
print("\n" + "=" * 70)
print("METHOD 2: Preserving Structure")
print("=" * 70)

# Split by major delimiters but preserve them
parts = message.split()
decoded_structured = ""

for part in parts:
    # Remove trailing punctuation
    punct = ""
    while part and part[-1] in ',.{}':
        punct = part[-1] + punct
        part = part[:-1]
    
    # Decode the octal number
    try:
        decimal = int(part, 8)
        if 0 <= decimal <= 127:
            decoded_structured += chr(decimal)
        else:
            decoded_structured += f"[{decimal}]"
    except:
        decoded_structured += part
    
    # Add back punctuation
    decoded_structured += punct

print(f"\nDecoded: {decoded_structured}")

# Method 3: Try to identify flag pattern
print("\n" + "=" * 70)
print("METHOD 3: Extract Flag Pattern")
print("=" * 70)

# Find the part between { }
import re
flag_match = re.search(r'\{([^}]+)\}', message)
if flag_match:
    flag_octals = flag_match.group(1).split()
    flag_decoded = ""
    for octal in flag_octals:
        try:
            decimal = int(octal, 8)
            if 0 <= decimal <= 127:
                flag_decoded += chr(decimal)
            else:
                flag_decoded += f"[{decimal}]"
        except:
            flag_decoded += f"[?{octal}]"
    
    print(f"\nFlag content (between {{ }}): {flag_decoded}")
    print(f"\nPossible flag formats:")
    print(f"   CTF{{{flag_decoded}}}")
    print(f"   CIT{{{flag_decoded}}}")
    print(f"   FLAG{{{flag_decoded}}}")

# Method 4: Check if it's extended ASCII (0-255)
print("\n" + "=" * 70)
print("METHOD 4: Extended ASCII (0-255)")
print("=" * 70)

decoded_extended = ""
for octal in octal_numbers:
    try:
        decimal = int(octal, 8)
        if 0 <= decimal <= 255:
            decoded_extended += chr(decimal)
        else:
            decoded_extended += f"[{decimal}]"
    except:
        decoded_extended += f"[?{octal}]"

print(f"\nDecoded (extended): {decoded_extended}")

# Method 5: Try XOR with common keys
print("\n" + "=" * 70)
print("METHOD 5: XOR Decoding Attempts")
print("=" * 70)

# Convert octals to bytes
byte_values = []
for octal in octal_numbers:
    try:
        decimal = int(octal, 8)
        byte_values.append(decimal % 256)  # Keep in byte range
    except:
        pass

# Try XOR with common single-byte keys
common_keys = [
    ord('F'), ord('f'),  # Force
    ord('S'), ord('s'),  # Star Wars
    ord('Y'), ord('y'),  # Yoda
    ord('J'), ord('j'),  # Jedi
    42, 13, 32, 0
]

for key in common_keys:
    xor_decoded = ""
    for byte in byte_values:
        xor_decoded += chr(byte ^ key)
    
    # Check if it looks like readable text
    if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in xor_decoded):
        print(f"\nXOR with {key} ('{chr(key) if 32 <= key <= 126 else key}'): {xor_decoded}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
