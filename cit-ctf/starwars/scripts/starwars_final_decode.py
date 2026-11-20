#!/usr/bin/env python3
"""
Star Wars - Final Decode Analysis
The octal escape approach showed some readable text!
"""

import re

print("=" * 70)
print("STAR WARS - FINAL DECODE")
print("=" * 70)

message = """095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"""

number_strings = re.findall(r'\d{3}', message)

print(f"\n📊 {len(number_strings)} 3-digit groups")

# The escape sequence approach gave us something
# Let's analyze it more carefully
print("\n" + "=" * 70)
print("DETAILED OCTAL ESCAPE ANALYSIS")
print("=" * 70)

# Build the escape string
escape_str = ''.join(f"\\{num}" for num in number_strings)

# Decode it
try:
    decoded = escape_str.encode().decode('unicode_escape')
    print(f"\nFull decoded string:")
    print(f"{decoded}")
    print(f"\nLength: {len(decoded)} characters")
    
    # Show hex representation
    print(f"\nHex representation:")
    hex_str = decoded.encode('latin-1').hex()
    print(f"{hex_str}")
    
    # Show character by character
    print(f"\nCharacter breakdown:")
    for i, c in enumerate(decoded):
        code = ord(c)
        if 32 <= code <= 126:
            print(f"   [{i}] '{c}' (ASCII {code})")
        else:
            print(f"   [{i}] [non-printable] (code {code})")
    
    # Try to extract flag
    print(f"\n" + "=" * 70)
    print("FLAG EXTRACTION")
    print("=" * 70)
    
    # Look for { and }
    if '{' in decoded:
        start = decoded.index('{')
        if '}' in decoded[start:]:
            end = decoded.index('}', start)
            flag_content = decoded[start+1:end]
            print(f"\n🏁 FLAG FOUND!")
            print(f"   Content: {flag_content}")
            print(f"   Full: {{{flag_content}}}")
            
            # Show hex of flag content
            flag_hex = flag_content.encode('latin-1').hex()
            print(f"   Hex: {flag_hex}")
    
    # Try to clean up the string - remove non-printable
    cleaned = ''.join(c if 32 <= ord(c) <= 126 else ' ' for c in decoded)
    print(f"\n" + "=" * 70)
    print("CLEANED STRING (printable only)")
    print("=" * 70)
    print(f"{cleaned}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Alternative: Try treating as raw bytes
print("\n" + "=" * 70)
print("RAW BYTES INTERPRETATION")
print("=" * 70)

# Convert each 3-digit group to a byte
byte_values = []
for num_str in number_strings:
    # Try as octal first
    if all(c in '01234567' for c in num_str):
        byte_values.append(int(num_str, 8))
    else:
        # Use decimal but mod 256
        byte_values.append(int(num_str) % 256)

print(f"Byte values: {byte_values[:20]}...")

# Try to decode as UTF-8
try:
    decoded_utf8 = bytes(byte_values).decode('utf-8', errors='ignore')
    print(f"\nUTF-8 decode: {decoded_utf8}")
except:
    pass

# Try to decode as Latin-1
try:
    decoded_latin1 = bytes(byte_values).decode('latin-1')
    print(f"\nLatin-1 decode: {decoded_latin1}")
    
    if '{' in decoded_latin1 and '}' in decoded_latin1:
        flag_match = re.search(r'\{([^}]+)\}', decoded_latin1)
        if flag_match:
            print(f"\n🏁 FLAG: {{{flag_match.group(1)}}}")
except:
    pass

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
