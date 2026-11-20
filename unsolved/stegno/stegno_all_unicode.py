#!/usr/bin/env python3
"""
Found U+202C (POP DIRECTIONAL FORMATTING) in the text!
Let's analyze ALL Unicode characters
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

print("="*70)
print("COMPLETE UNICODE ANALYSIS")
print("="*70)

# Get all unique codepoints
unique_codepoints = sorted(set(ord(c) for c in text))
print(f"\n[*] Unique codepoints: {len(unique_codepoints)}")

# Categorize them
invisible_chars = {}
for cp in unique_codepoints:
    if cp < 32 or cp > 126:
        char = chr(cp)
        count = text.count(char)
        invisible_chars[cp] = (char, count)
        print(f"    U+{cp:04X} ({cp:5d}): {count:3d} occurrences")

# Extract ALL invisible characters in order
print("\n[*] Extracting ALL invisible characters:")
invisible_sequence = []
for char in text:
    cp = ord(char)
    if cp < 32 or cp > 126:
        invisible_sequence.append(char)

print(f"    Total: {len(invisible_sequence)} invisible chars")

# Show first 50
print(f"\n[*] First 50 invisible characters:")
for i, char in enumerate(invisible_sequence[:50]):
    print(f"U+{ord(char):04X}", end=' ')
    if (i + 1) % 10 == 0:
        print()

# Try decoding with U+202C included
print("\n\n[*] Trying decode with U+202C (POP DIRECTIONAL FORMATTING):")

# Define all characters
ZWNJ = '\u200C'  # 8204
ZWJ = '\u200D'   # 8205
PDF = '\u202C'   # 8236 - POP DIRECTIONAL FORMATTING
BOM = '\uFEFF'   # 65279

# Try PDF as separator
groups = []
current = []
for c in invisible_sequence:
    if c == PDF:
        if current:
            groups.append(current)
            current = []
    else:
        current.append(c)
if current:
    groups.append(current)

print(f"    Using PDF as separator: {len(groups)} groups")

# Decode with remaining chars as binary
decoded = ''
for i, group in enumerate(groups[:30]):
    # Filter out BOM, use ZWNJ/ZWJ as binary
    binary_chars = [c for c in group if c in [ZWNJ, ZWJ]]
    if binary_chars:
        binary = ''.join('0' if c == ZWNJ else '1' for c in binary_chars)
        try:
            char_code = int(binary, 2)
            if 32 <= char_code <= 126:
                char = chr(char_code)
                decoded += char
                if i < 20:
                    print(f"    Group {i+1}: {binary:8s} = {char_code:3d} = '{char}'")
        except:
            pass

print(f"\n    Decoded: {decoded}")

if 'CIT{' in decoded:
    print(f"\n{'='*70}")
    print(f"[!!!] FLAG FOUND: {decoded}")
    print(f"{'='*70}")

print("\n" + "="*70)
