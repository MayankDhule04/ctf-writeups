#!/usr/bin/env python3
"""
Decode using BOM as separator - we got "AA" which suggests we're on the right track
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

ZWNJ = '\u200C'
ZWJ = '\u200D'
BOM = '\uFEFF'

zw_sequence = [c for c in text if c in [ZWNJ, ZWJ, BOM]]

print("="*70)
print("BOM AS SEPARATOR DECODER")
print("="*70)

# Split by BOM
groups = []
current = []
for c in zw_sequence:
    if c == BOM:
        if current:
            groups.append(current)
            current = []
    else:
        current.append(c)
if current:
    groups.append(current)

print(f"\n[*] Found {len(groups)} groups separated by BOM")

# Try both binary mappings
for mapping_name, char0, char1 in [("ZWNJ=0, ZWJ=1", ZWNJ, ZWJ), ("ZWJ=0, ZWNJ=1", ZWJ, ZWNJ)]:
    print(f"\n[*] Mapping: {mapping_name}")
    
    decoded = ''
    for i, group in enumerate(groups):
        binary = ''.join('0' if c == char0 else '1' for c in group)
        
        if binary:
            try:
                char_code = int(binary, 2)
                char = chr(char_code) if 0 < char_code <= 127 else '?'
                decoded += char
                
                if i < 30:  # Show first 30 groups
                    print(f"    Group {i+1:2d}: {binary:12s} = {char_code:3d} = '{char}'")
            except Exception as e:
                print(f"    Group {i+1}: Error - {e}")
    
    print(f"\n    Full decoded: {decoded}")
    
    if 'CIT{' in decoded:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND!")
        print(f"{'='*70}")
        print(f"FLAG: {decoded}")
        print(f"{'='*70}")
        
        # Extract clean flag
        start = decoded.find('CIT{')
        end = decoded.find('}', start) + 1
        if start != -1 and end > start:
            flag = decoded[start:end]
            print(f"\nCLEAN FLAG: {flag}")
        exit(0)

print("\n" + "="*70)
