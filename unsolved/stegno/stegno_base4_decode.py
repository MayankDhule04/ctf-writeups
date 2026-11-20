#!/usr/bin/env python3
"""
Base-4 encoding with 4 invisible characters:
- U+200C (ZWNJ)
- U+200D (ZWJ)
- U+202C (PDF)
- U+FEFF (BOM)
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

ZWNJ = '\u200C'  # 8204
ZWJ = '\u200D'   # 8205
PDF = '\u202C'   # 8236
BOM = '\uFEFF'   # 65279

# Extract invisible sequence
invisible_sequence = [c for c in text if c in [ZWNJ, ZWJ, PDF, BOM]]

print("="*70)
print("BASE-4 DECODER (4 invisible characters)")
print("="*70)
print(f"\n[*] Total invisible chars: {len(invisible_sequence)}")

# Try all 24 possible mappings (4! = 24)
from itertools import permutations

chars = [ZWNJ, ZWJ, PDF, BOM]
char_names = ['ZWNJ', 'ZWJ', 'PDF', 'BOM']

best_results = []

for perm in permutations(range(4)):
    mapping = {chars[i]: str(perm[i]) for i in range(4)}
    
    # Convert to base-4 string
    base4 = ''.join(mapping[c] for c in invisible_sequence)
    
    # Try different group sizes
    for group_size in [3, 4, 5]:
        decoded = ''
        valid_chars = 0
        
        for i in range(0, len(base4), group_size):
            group = base4[i:i+group_size]
            if len(group) == group_size:
                try:
                    # Convert base-4 to decimal
                    decimal = int(group, 4)
                    if 32 <= decimal <= 126:
                        decoded += chr(decimal)
                        valid_chars += 1
                    elif decimal == 0:
                        continue
                    else:
                        if valid_chars > 0:
                            break
                except:
                    break
        
        if valid_chars >= 5:
            score = valid_chars
            if 'CIT{' in decoded:
                score += 1000
            if '}' in decoded:
                score += 100
            
            best_results.append({
                'mapping': perm,
                'group_size': group_size,
                'decoded': decoded,
                'score': score,
                'valid_chars': valid_chars
            })

# Sort by score
best_results.sort(key=lambda x: x['score'], reverse=True)

print("\n[*] Top 10 Results:")
for i, result in enumerate(best_results[:10]):
    perm = result['mapping']
    mapping_str = ', '.join(f"{char_names[j]}={perm[j]}" for j in range(4))
    
    print(f"\n{i+1}. Group size {result['group_size']}, Valid: {result['valid_chars']}, Score: {result['score']}")
    print(f"   Mapping: {mapping_str}")
    print(f"   Decoded: {result['decoded'][:80]}")
    
    if 'CIT{' in result['decoded']:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND!")
        print(f"{'='*70}")
        print(f"FLAG: {result['decoded']}")
        print(f"{'='*70}")
        
        # Extract clean flag
        start = result['decoded'].find('CIT{')
        end = result['decoded'].find('}', start) + 1
        if start != -1 and end > start:
            flag = result['decoded'][start:end]
            print(f"\nCLEAN FLAG: {flag}")
        exit(0)

print("\n" + "="*70)
