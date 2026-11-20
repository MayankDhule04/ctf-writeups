#!/usr/bin/env python3
"""
Maybe the BOM positions themselves encode the message?
Or the LENGTH of groups between BOMs?
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

ZWNJ = '\u200C'
ZWJ = '\u200D'
BOM = '\uFEFF'

zw_sequence = [c for c in text if c in [ZWNJ, ZWJ, BOM]]

print("="*70)
print("BOM POSITION / GROUP LENGTH ANALYSIS")
print("="*70)

# Get BOM positions
bom_positions = [i for i, c in enumerate(zw_sequence) if c == BOM]
print(f"\n[*] BOM positions: {bom_positions}")

# Get group lengths
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

group_lengths = [len(g) for g in groups]
print(f"\n[*] Group lengths: {group_lengths}")

# Try decoding group lengths as ASCII
print("\n[*] Group lengths as ASCII:")
decoded_lengths = ''.join(chr(l) if 32 <= l <= 126 else '?' for l in group_lengths)
print(f"    {decoded_lengths}")

if 'CIT{' in decoded_lengths:
    print(f"\n[!!!] FLAG FOUND: {decoded_lengths}")

# Try BOM positions as ASCII
print("\n[*] BOM positions as ASCII:")
decoded_pos = ''.join(chr(p) if 32 <= p <= 126 else '?' for p in bom_positions)
print(f"    {decoded_pos}")

# Try differences between BOM positions
print("\n[*] Differences between BOM positions:")
diffs = [bom_positions[i+1] - bom_positions[i] for i in range(len(bom_positions)-1)]
print(f"    Differences: {diffs}")
decoded_diffs = ''.join(chr(d) if 32 <= d <= 126 else '?' for d in diffs)
print(f"    As ASCII: {decoded_diffs}")

if 'CIT{' in decoded_diffs:
    print(f"\n[!!!] FLAG FOUND: {decoded_diffs}")

# Maybe it's the count of ZWNJ vs ZWJ in each group?
print("\n[*] ZWNJ count in each group:")
zwnj_counts = [g.count(ZWNJ) for g in groups]
print(f"    Counts: {zwnj_counts}")
decoded_zwnj = ''.join(chr(c) if 32 <= c <= 126 else '?' for c in zwnj_counts)
print(f"    As ASCII: {decoded_zwnj}")

if 'CIT{' in decoded_zwnj:
    print(f"\n[!!!] FLAG FOUND: {decoded_zwnj}")

print("\n[*] ZWJ count in each group:")
zwj_counts = [g.count(ZWJ) for g in groups]
print(f"    Counts: {zwj_counts}")
decoded_zwj = ''.join(chr(c) if 32 <= c <= 126 else '?' for c in zwj_counts)
print(f"    As ASCII: {decoded_zwj}")

if 'CIT{' in decoded_zwj:
    print(f"\n[!!!] FLAG FOUND: {decoded_zwj}")

# Try ratio or combination
print("\n[*] Trying combinations:")
for i in range(min(len(groups), 30)):
    zwnj_c = groups[i].count(ZWNJ)
    zwj_c = groups[i].count(ZWJ)
    total = len(groups[i])
    
    print(f"    Group {i+1}: len={total:2d}, ZWNJ={zwnj_c:2d}, ZWJ={zwj_c:2d}", end="")
    
    # Try as ASCII
    for val in [total, zwnj_c, zwj_c, zwnj_c+zwj_c]:
        if 32 <= val <= 126:
            print(f" -> '{chr(val)}'", end="")
    print()

print("\n" + "="*70)
