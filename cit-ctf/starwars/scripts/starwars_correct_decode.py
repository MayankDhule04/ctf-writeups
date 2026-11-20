#!/usr/bin/env python3
"""
Star Wars - Correct Decoding
Treat the numbers as they would appear in a string literal
"""

print("=" * 70)
print("STAR WARS - CORRECT DECODING")
print("=" * 70)

# The original message with structure preserved
message_with_structure = r"095 181 145 039 245 091 212 232 123 220 167 069 091 208 245 164 245 145 123 094, 062 150 094 172 083 135 096 153 002 208 096 172. 201 005 019 {131 091 090 053 095 218 238 211 091 004 201 182 135 245 167 074 090 145 096 238}"

# Build a Python string literal with octal escapes
import re
numbers = re.findall(r'\d{3}', message_with_structure)

print(f"📊 {len(numbers)} numbers")

# Create string with proper octal escapes
octal_string_literal = '"' + ''.join(f'\\{n}' for n in numbers) + '"'

print(f"\nString literal: {octal_string_literal[:80]}...")

# Evaluate it to get the actual string
try:
    decoded = eval(octal_string_literal)
    print(f"\n✅ DECODED STRING:")
    print(f"{decoded}")
    print(f"\nLength: {len(decoded)}")
    
    # Extract flag if present
    flag_match = re.search(r'\{([^}]+)\}', decoded)
    if flag_match:
        flag_content = flag_match.group(1)
        print(f"\n🏁 FLAG FOUND!")
        print(f"   {{{flag_content}}}")
        
        # Try common flag formats
        print(f"\n   Possible formats:")
        print(f"   CTF{{{flag_content}}}")
        print(f"   CIT{{{flag_content}}}")
        print(f"   FLAG{{{flag_content}}}")
    else:
        print(f"\n⚠️  No flag pattern found in decoded string")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

# Also try with the structure (commas, periods, braces) preserved
print("\n" + "=" * 70)
print("WITH STRUCTURE PRESERVED")
print("=" * 70)

# Manually parse preserving structure
parts = message_with_structure.split()
decoded_parts = []

for part in parts:
    # Extract numbers from this part
    nums = re.findall(r'\d{3}', part)
    if nums:
        # Decode these numbers
        decoded_part = ""
        for n in nums:
            try:
                # Treat as octal escape
                char = eval(f'"{chr(int(n, 8))}"')
                decoded_part += char
            except:
                decoded_part += '?'
        decoded_parts.append(decoded_part)

decoded_with_structure = ' '.join(decoded_parts)
print(f"\nDecoded: {decoded_with_structure}")

print("\n" + "=" * 70)
