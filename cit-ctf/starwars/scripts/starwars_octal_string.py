#!/usr/bin/env python3
"""
Star Wars - Treat number strings as octal literals
E.g., "095" -> treat as octal \095 -> decimal 61 -> '='
"""

import re

print("=" * 70)
print("STAR WARS - OCTAL STRING INTERPRETATION")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

# Extract the 3-digit groups as strings
number_strings = re.findall(r'\d{3}', message)

print(f"\n📊 Found {len(number_strings)} 3-digit groups")
print(f"   First 10: {number_strings[:10]}")

# Approach 1: Treat each 3-digit string as octal
print("\n" + "=" * 70)
print("APPROACH 1: Each 3-digit group as Octal")
print("=" * 70)

decoded = ""
for num_str in number_strings:
    try:
        # Parse as octal (base 8)
        # But some have 8 or 9, so they're invalid octal
        # Let's try anyway and skip invalid ones
        if all(c in '01234567' for c in num_str):
            octal_val = int(num_str, 8)
            if 32 <= octal_val <= 126:
                decoded += chr(octal_val)
            else:
                decoded += f"[{octal_val}]"
        else:
            # Invalid octal, try as decimal
            decimal_val = int(num_str)
            if 32 <= decimal_val <= 126:
                decoded += chr(decimal_val)
            else:
                decoded += '.'
    except:
        decoded += '?'

print(f"Decoded: {decoded}")

# Approach 2: Treat as escape sequences (like \095)
print("\n" + "=" * 70)
print("APPROACH 2: As Escape Sequences")
print("=" * 70)

# Build escape string
escape_string = ''.join(f"\\{num}" for num in number_strings)
print(f"Escape string: {escape_string[:100]}...")

# Try to decode it
try:
    decoded = escape_string.encode().decode('unicode_escape')
    print(f"Decoded: {decoded}")
except Exception as e:
    print(f"Failed: {e}")

# Approach 3: Mixed interpretation - valid octal as octal, others as decimal
print("\n" + "=" * 70)
print("APPROACH 3: Smart Mixed Interpretation")
print("=" * 70)

decoded = ""
for num_str in number_strings:
    # Check if it's valid octal (no 8 or 9)
    if all(c in '01234567' for c in num_str):
        # Treat as octal
        val = int(num_str, 8)
        if 32 <= val <= 126:
            decoded += chr(val)
        else:
            decoded += '.'
    else:
        # Treat as decimal
        val = int(num_str)
        if 32 <= val <= 126:
            decoded += chr(val)
        else:
            decoded += '.'

print(f"Decoded: {decoded}")

# Check if it contains flag
if '{' in decoded and '}' in decoded:
    flag_match = re.search(r'\{([^}]+)\}', decoded)
    if flag_match:
        print(f"\n🏁 FLAG FOUND: {{{flag_match.group(1)}}}")

# Approach 4: Try Python's bytes literal interpretation
print("\n" + "=" * 70)
print("APPROACH 4: Python Bytes Literal")
print("=" * 70)

# Create a bytes literal string
bytes_literal = 'b"' + ''.join(f"\\{num}" for num in number_strings) + '"'
print(f"Bytes literal: {bytes_literal[:100]}...")

try:
    # Evaluate it (be careful with eval!)
    decoded_bytes = eval(bytes_literal)
    decoded = decoded_bytes.decode('utf-8', errors='ignore')
    print(f"Decoded: {decoded}")
    
    if '{' in decoded and '}' in decoded:
        flag_match = re.search(r'\{([^}]+)\}', decoded)
        if flag_match:
            print(f"\n🏁 FLAG FOUND: {{{flag_match.group(1)}}}")
except Exception as e:
    print(f"Failed: {e}")

# Approach 5: Maybe they're meant to be read as \ooo in a string
print("\n" + "=" * 70)
print("APPROACH 5: Direct Octal Escape Interpretation")
print("=" * 70)

# Build string with octal escapes
octal_string = ''.join(f"\\{num}" for num in number_strings)

# Try to interpret it
try:
    # Use codecs to decode
    import codecs
    decoded = codecs.decode(octal_string, 'unicode_escape')
    print(f"Decoded: {decoded}")
    
    if '{' in decoded and '}' in decoded:
        flag_match = re.search(r'\{([^}]+)\}', decoded)
        if flag_match:
            print(f"\n🏁 FLAG FOUND: {{{flag_match.group(1)}}}")
except Exception as e:
    print(f"Failed: {e}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
