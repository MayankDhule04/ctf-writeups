#!/usr/bin/env python3
"""
Stegzero-style decoder
Based on https://stegzero.com/ algorithm
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Zero-width characters used by stegzero
ZWSP = '\u200B'  # Zero Width Space
ZWNJ = '\u200C'  # Zero Width Non-Joiner
ZWJ = '\u200D'   # Zero Width Joiner
BOM = '\uFEFF'   # Zero Width No-Break Space

print("="*70)
print("STEGZERO-STYLE DECODER")
print("="*70)

# Check which characters are present
chars_present = {}
for char in [ZWSP, ZWNJ, ZWJ, BOM]:
    count = text.count(char)
    if count > 0:
        chars_present[char] = count
        print(f"U+{ord(char):04X}: {count} occurrences")

# Extract zero-width sequence
zw_sequence = []
for char in text:
    if char in chars_present:
        zw_sequence.append(char)

print(f"\nTotal zero-width chars: {len(zw_sequence)}")

# Stegzero typically uses binary encoding
# Try different character assignments
print("\n[*] Trying binary encodings:")

# If only 2 chars, straightforward binary
if len(chars_present) == 2:
    chars = list(chars_present.keys())
    binary = ''.join('0' if c == chars[0] else '1' for c in zw_sequence)
    
    decoded = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            decoded += chr(int(byte, 2))
    
    print(f"    {chars[0]} = 0, {chars[1]} = 1")
    print(f"    Decoded: {decoded}")
    
    if 'CIT{' in decoded:
        print(f"\n[!!!] FLAG FOUND: {decoded}")

# If 3 chars, one might be separator
elif len(chars_present) == 3:
    chars = list(chars_present.keys())
    
    # Try each as separator
    for sep_idx, separator in enumerate(chars):
        other_chars = [c for c in chars if c != separator]
        
        print(f"\n    Using U+{ord(separator):04X} as separator")
        
        # Split by separator
        groups = []
        current = []
        for c in zw_sequence:
            if c == separator:
                if current:
                    groups.append(current)
                    current = []
            else:
                current.append(c)
        if current:
            groups.append(current)
        
        # Decode each group as binary
        decoded = ''
        for group in groups:
            binary = ''.join('0' if c == other_chars[0] else '1' for c in group)
            if binary:
                try:
                    char_code = int(binary, 2)
                    if 0 < char_code <= 127:
                        decoded += chr(char_code)
                except:
                    pass
        
        print(f"    Decoded: {decoded[:80]}")
        
        if 'CIT{' in decoded:
            print(f"\n{'='*70}")
            print(f"[!!!] FLAG FOUND!")
            print(f"{'='*70}")
            print(f"FLAG: {decoded}")
            print(f"{'='*70}")
            exit(0)

print("\n" + "="*70)
