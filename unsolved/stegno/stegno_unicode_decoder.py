#!/usr/bin/env python3
"""
"There's no room left" - Unicode Steganography Decoder
SHA1: 0f425ef58c8922ef1bad11929b317bc9d7b21a73

The hint "walls closing in digitally" + "no room left" suggests:
- Zero-width characters (invisible Unicode)
- Whitespace steganography

Common zero-width characters:
- U+200B: Zero Width Space (ZWSP)
- U+200C: Zero Width Non-Joiner (ZWNJ)  
- U+200D: Zero Width Joiner (ZWJ)
- U+FEFF: Zero Width No-Break Space (BOM)
- U+2060: Word Joiner
"""

import hashlib

file_path = "cit_stegno.txt"

print("="*70)
print("UNICODE STEGANOGRAPHY DECODER")
print("="*70)

# Read file
with open(file_path, 'rb') as f:
    data = f.read()
    sha1 = hashlib.sha1(data).hexdigest()
    print(f"\n[*] SHA1: {sha1}")
    if sha1 == "0f425ef58c8922ef1bad11929b317bc9d7b21a73":
        print(f"    ✓ SHA1 matches!")

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

print(f"\n[*] File size: {len(data)} bytes")
print(f"[*] Text length: {len(text)} characters")

# Define zero-width characters
zero_width_chars = {
    '\u200B': 'ZWSP (Zero Width Space)',
    '\u200C': 'ZWNJ (Zero Width Non-Joiner)',
    '\u200D': 'ZWJ (Zero Width Joiner)',
    '\uFEFF': 'BOM (Zero Width No-Break Space)',
    '\u2060': 'Word Joiner',
    '\u180E': 'Mongolian Vowel Separator',
}

# Count zero-width characters
print("\n[*] Zero-Width Character Analysis:")
zw_found = {}
for char in text:
    if char in zero_width_chars:
        zw_found[char] = zw_found.get(char, 0) + 1

if zw_found:
    for char, count in zw_found.items():
        print(f"    {zero_width_chars[char]}: {count} occurrences")
        print(f"      Unicode: U+{ord(char):04X}")
else:
    print("    No zero-width characters found")

# Extract zero-width characters as binary
print("\n[*] Extracting Zero-Width Characters:")
zw_sequence = []
for char in text:
    if char in zero_width_chars:
        zw_sequence.append(char)

print(f"    Found {len(zw_sequence)} zero-width characters")

# Try different binary mappings
print("\n[*] Binary Decoding Attempts:")

# Method 1: ZWSP=0, ZWNJ=1
if '\u200B' in zw_found and '\u200C' in zw_found:
    binary = ''.join('0' if c == '\u200B' else '1' for c in zw_sequence)
    print(f"\n    Method 1: ZWSP=0, ZWNJ=1")
    print(f"    Binary: {binary[:80]}...")
    
    # Convert to bytes
    try:
        # Pad to multiple of 8
        while len(binary) % 8 != 0:
            binary += '0'
        
        decoded = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            decoded += chr(int(byte, 2))
        
        print(f"    Decoded: {decoded}")
        
        if 'CIT{' in decoded:
            print(f"\n    [!!!] FLAG FOUND: {decoded}")
    except Exception as e:
        print(f"    Error: {e}")

# Method 2: Try all combinations
print("\n[*] Trying All Character Mappings:")
unique_chars = list(zw_found.keys())
if len(unique_chars) >= 2:
    # Try first two as 0 and 1
    char0, char1 = unique_chars[0], unique_chars[1]
    binary = ''.join('0' if c == char0 else '1' if c == char1 else '' for c in zw_sequence)
    
    print(f"    {zero_width_chars[char0]} = 0")
    print(f"    {zero_width_chars[char1]} = 1")
    print(f"    Binary: {binary[:80]}...")
    
    try:
        while len(binary) % 8 != 0:
            binary += '0'
        
        decoded = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            decoded += chr(int(byte, 2))
        
        print(f"    Decoded: {decoded}")
        
        if 'CIT{' in decoded:
            print(f"\n    [!!!] FLAG FOUND: {decoded}")
    except Exception as e:
        print(f"    Error: {e}")

# Method 3: Show raw Unicode codepoints
print("\n[*] Raw Zero-Width Character Sequence:")
for i, char in enumerate(zw_sequence[:50]):  # First 50
    print(f"U+{ord(char):04X}", end=' ')
    if (i + 1) % 10 == 0:
        print()

# Method 4: Try as base-N encoding
if len(unique_chars) > 2:
    print(f"\n[*] Detected {len(unique_chars)} unique zero-width chars")
    print(f"    Possible base-{len(unique_chars)} encoding")

# Show visible text without zero-width chars
print("\n[*] Visible Text (without zero-width chars):")
visible = ''.join(c for c in text if c not in zero_width_chars)
print(f"    {visible}")

print("\n" + "="*70)
