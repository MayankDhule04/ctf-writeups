#!/usr/bin/env python3
"""
Unicode Steganography - Ternary (Base-3) Decoder

Three unique zero-width characters:
- U+200C (ZWNJ) = 0
- U+200D (ZWJ) = 1  
- U+FEFF (BOM) = 2
"""

file_path = "cit_stegno.txt"

print("="*70)
print("TERNARY UNICODE STEGANOGRAPHY DECODER")
print("="*70)

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Define zero-width characters
zw_chars = {
    '\u200C': 'ZWNJ',
    '\u200D': 'ZWJ',
    '\uFEFF': 'BOM',
}

# Extract zero-width sequence
zw_sequence = [c for c in text if c in zw_chars]
print(f"\n[*] Found {len(zw_sequence)} zero-width characters")

# Try all 6 possible mappings (3! = 6)
mappings = [
    {'\u200C': '0', '\u200D': '1', '\uFEFF': '2'},
    {'\u200C': '0', '\u200D': '2', '\uFEFF': '1'},
    {'\u200C': '1', '\u200D': '0', '\uFEFF': '2'},
    {'\u200C': '1', '\u200D': '2', '\uFEFF': '0'},
    {'\u200C': '2', '\u200D': '0', '\uFEFF': '1'},
    {'\u200C': '2', '\u200D': '1', '\uFEFF': '0'},
]

for idx, mapping in enumerate(mappings):
    print(f"\n[*] Mapping {idx+1}:")
    for char, val in mapping.items():
        print(f"    U+{ord(char):04X} ({zw_chars[char]}) = {val}")
    
    # Convert to ternary string
    ternary = ''.join(mapping[c] for c in zw_sequence)
    print(f"    Ternary: {ternary[:60]}...")
    
    # Convert ternary to decimal to ASCII
    try:
        # Try grouping by different sizes
        for group_size in [5, 6, 7, 8]:
            decoded = ''
            valid = True
            
            for i in range(0, len(ternary), group_size):
                group = ternary[i:i+group_size]
                if len(group) < group_size:
                    break
                
                # Convert ternary to decimal
                decimal = int(group, 3)
                
                # Check if valid ASCII
                if 32 <= decimal <= 126:
                    decoded += chr(decimal)
                else:
                    valid = False
                    break
            
            if valid and len(decoded) > 5:
                print(f"    Group size {group_size}: {decoded}")
                
                if 'CIT{' in decoded:
                    print(f"\n{'='*70}")
                    print(f"[!!!] FLAG FOUND!")
                    print(f"{'='*70}")
                    print(f"FLAG: {decoded}")
                    print(f"{'='*70}")
                    exit(0)
    except Exception as e:
        pass

# Try binary encoding (ignore one character)
print("\n[*] Trying Binary Encoding (2 chars only):")
for ignore_char in ['\u200C', '\u200D', '\uFEFF']:
    print(f"\n    Ignoring U+{ord(ignore_char):04X} ({zw_chars[ignore_char]})")
    
    # Use remaining two chars as 0 and 1
    remaining = [c for c in ['\u200C', '\u200D', '\uFEFF'] if c != ignore_char]
    
    binary = ''
    for c in zw_sequence:
        if c == remaining[0]:
            binary += '0'
        elif c == remaining[1]:
            binary += '1'
        # Skip the ignored character
    
    print(f"    Binary: {binary[:60]}...")
    
    # Convert to ASCII
    try:
        decoded = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                decoded += chr(int(byte, 2))
        
        print(f"    Decoded: {decoded[:80]}")
        
        if 'CIT{' in decoded:
            print(f"\n{'='*70}")
            print(f"[!!!] FLAG FOUND!")
            print(f"{'='*70}")
            print(f"FLAG: {decoded}")
            print(f"{'='*70}")
            exit(0)
    except Exception as e:
        pass

print("\n" + "="*70)
print("[!] Flag not found with standard methods")
print("[!] May need custom decoding logic")
print("="*70)
