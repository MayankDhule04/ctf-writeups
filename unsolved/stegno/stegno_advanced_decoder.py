#!/usr/bin/env python3
"""
Advanced Unicode Steganography Decoder
Trying different grouping and encoding methods
"""

file_path = "cit_stegno.txt"

print("="*70)
print("ADVANCED UNICODE STEGANOGRAPHY DECODER")
print("="*70)

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Define characters
ZWNJ = '\u200C'  # U+200C
ZWJ = '\u200D'   # U+200D
BOM = '\uFEFF'   # U+FEFF

# Extract sequence
zw_sequence = [c for c in text if c in [ZWNJ, ZWJ, BOM]]
print(f"\n[*] Total zero-width chars: {len(zw_sequence)}")
print(f"    ZWNJ (U+200C): {zw_sequence.count(ZWNJ)}")
print(f"    ZWJ  (U+200D): {zw_sequence.count(ZWJ)}")
print(f"    BOM  (U+FEFF): {zw_sequence.count(BOM)}")

# Method 1: BOM as separator, ZWNJ/ZWJ as binary
print("\n[*] Method 1: BOM as separator, ZWNJ=0, ZWJ=1")
groups = []
current_group = []

for char in zw_sequence:
    if char == BOM:
        if current_group:
            groups.append(current_group)
            current_group = []
    else:
        current_group.append(char)

if current_group:
    groups.append(current_group)

print(f"    Found {len(groups)} groups")

decoded = ''
for i, group in enumerate(groups[:20]):  # First 20 groups
    binary = ''.join('0' if c == ZWNJ else '1' for c in group)
    if binary:
        try:
            decimal = int(binary, 2)
            if 32 <= decimal <= 126:
                char = chr(decimal)
                decoded += char
                print(f"    Group {i+1}: {binary:8s} = {decimal:3d} = '{char}'")
            else:
                print(f"    Group {i+1}: {binary:8s} = {decimal:3d} (out of range)")
        except:
            pass

if decoded:
    print(f"\n    Decoded: {decoded}")
    if 'CIT{' in decoded:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND: {decoded}")
        print(f"{'='*70}")

# Method 2: Groups of 4 ternary digits
print("\n[*] Method 2: Groups of 4 ternary (ZWNJ=0, ZWJ=1, BOM=2)")
mapping = {ZWNJ: '0', ZWJ: '1', BOM: '2'}
ternary = ''.join(mapping[c] for c in zw_sequence)

decoded2 = ''
for i in range(0, len(ternary), 4):
    group = ternary[i:i+4]
    if len(group) == 4:
        try:
            decimal = int(group, 3)
            if 32 <= decimal <= 126:
                decoded2 += chr(decimal)
        except:
            pass

if decoded2:
    print(f"    Decoded: {decoded2}")
    if 'CIT{' in decoded2:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND: {decoded2}")
        print(f"{'='*70}")

# Method 3: Groups of 5 ternary
print("\n[*] Method 3: Groups of 5 ternary")
decoded3 = ''
for i in range(0, len(ternary), 5):
    group = ternary[i:i+5]
    if len(group) == 5:
        try:
            decimal = int(group, 3)
            if 32 <= decimal <= 126:
                decoded3 += chr(decimal)
        except:
            pass

if decoded3:
    print(f"    Decoded: {decoded3}")
    if 'CIT{' in decoded3:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND: {decoded3}")
        print(f"{'='*70}")

# Method 4: Try different ternary mappings with group size 5
print("\n[*] Method 4: All ternary mappings with group size 5")
all_mappings = [
    {ZWNJ: '0', ZWJ: '1', BOM: '2'},
    {ZWNJ: '0', ZWJ: '2', BOM: '1'},
    {ZWNJ: '1', ZWJ: '0', BOM: '2'},
    {ZWNJ: '1', ZWJ: '2', BOM: '0'},
    {ZWNJ: '2', ZWJ: '0', BOM: '1'},
    {ZWNJ: '2', ZWJ: '1', BOM: '0'},
]

for map_idx, mapping in enumerate(all_mappings):
    ternary = ''.join(mapping[c] for c in zw_sequence)
    
    for group_size in [4, 5, 6]:
        decoded = ''
        for i in range(0, len(ternary), group_size):
            group = ternary[i:i+group_size]
            if len(group) == group_size:
                try:
                    decimal = int(group, 3)
                    if 32 <= decimal <= 126:
                        decoded += chr(decimal)
                    else:
                        break
                except:
                    break
        
        if 'CIT{' in decoded:
            print(f"\n    Mapping {map_idx+1}, Group size {group_size}:")
            print(f"    {mapping}")
            print(f"    Decoded: {decoded}")
            print(f"\n{'='*70}")
            print(f"[!!!] FLAG FOUND: {decoded}")
            print(f"{'='*70}")
            exit(0)

print("\n" + "="*70)
