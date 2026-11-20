#!/usr/bin/env python3
"""
Final Unicode Steganography Decoder
Comprehensive attempt with all methods
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

ZWNJ = '\u200C'
ZWJ = '\u200D'
BOM = '\uFEFF'

zw_sequence = [c for c in text if c in [ZWNJ, ZWJ, BOM]]

print("="*70)
print("COMPREHENSIVE UNICODE STEGANOGRAPHY DECODER")
print("="*70)
print(f"\n[*] Sequence length: {len(zw_sequence)}")

# Try all possible mappings and group sizes
all_mappings = [
    {ZWNJ: '0', ZWJ: '1', BOM: '2'},
    {ZWNJ: '0', ZWJ: '2', BOM: '1'},
    {ZWNJ: '1', ZWJ: '0', BOM: '2'},
    {ZWNJ: '1', ZWJ: '2', BOM: '0'},
    {ZWNJ: '2', ZWJ: '0', BOM: '1'},
    {ZWNJ: '2', ZWJ: '1', BOM: '0'},
]

best_results = []

for map_idx, mapping in enumerate(all_mappings):
    ternary = ''.join(mapping[c] for c in zw_sequence)
    
    for group_size in range(3, 9):  # Try group sizes 3-8
        decoded = ''
        valid_chars = 0
        
        for i in range(0, len(ternary) - group_size + 1, group_size):
            group = ternary[i:i+group_size]
            if len(group) == group_size:
                try:
                    decimal = int(group, 3)
                    if 32 <= decimal <= 126:
                        decoded += chr(decimal)
                        valid_chars += 1
                    elif decimal == 0:  # Allow null
                        continue
                    else:
                        # Stop if we hit invalid char
                        if valid_chars > 0:
                            break
                except:
                    break
        
        # Check if we found something promising
        if valid_chars >= 5:
            score = valid_chars
            if 'CIT{' in decoded:
                score += 1000
            if '}' in decoded:
                score += 100
            
            best_results.append({
                'mapping': map_idx + 1,
                'group_size': group_size,
                'decoded': decoded,
                'score': score,
                'valid_chars': valid_chars
            })

# Sort by score
best_results.sort(key=lambda x: x['score'], reverse=True)

print("\n[*] Top 10 Results:")
for i, result in enumerate(best_results[:10]):
    print(f"\n{i+1}. Mapping {result['mapping']}, Group size {result['group_size']}")
    print(f"   Valid chars: {result['valid_chars']}, Score: {result['score']}")
    print(f"   Decoded: {result['decoded'][:100]}")
    
    if 'CIT{' in result['decoded']:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND!")
        print(f"{'='*70}")
        print(f"FLAG: {result['decoded']}")
        print(f"{'='*70}")
        
        # Extract just the flag
        start = result['decoded'].find('CIT{')
        end = result['decoded'].find('}', start) + 1
        if start != -1 and end > start:
            flag = result['decoded'][start:end]
            print(f"\nExtracted FLAG: {flag}")
        break

# Also try with offsets
print("\n\n[*] Trying with offsets (skip first N characters):")
for offset in range(1, 5):
    for map_idx, mapping in enumerate(all_mappings):
        ternary = ''.join(mapping[c] for c in zw_sequence[offset:])
        
        for group_size in [4, 5, 6]:
            decoded = ''
            for i in range(0, len(ternary), group_size):
                group = ternary[i:i+group_size]
                if len(group) == group_size:
                    try:
                        decimal = int(group, 3)
                        if 32 <= decimal <= 126:
                            decoded += chr(decimal)
                    except:
                        pass
            
            if 'CIT{' in decoded:
                print(f"\n[!!!] FOUND with offset {offset}, mapping {map_idx+1}, group {group_size}")
                print(f"FLAG: {decoded}")
                exit(0)

print("\n" + "="*70)
