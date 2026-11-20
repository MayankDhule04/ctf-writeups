#!/usr/bin/env python3
"""
Wiretap - Proper T9 Decoding
In T9 multi-tap: repeated presses = different letters, * = space/separator
"""

sequence = "14155551998887*7788*707*87*77*8*7**8877**8**787"

print("="*70)
print("WIRETAP - T9 MULTI-TAP DECODER")
print("="*70)

# T9 keypad mapping
t9_map = {
    '0': ' ',
    '1': '.,?!',
    '2': 'ABC',
    '3': 'DEF',
    '4': 'GHI',
    '5': 'JKL',
    '6': 'MNO',
    '7': 'PQRS',
    '8': 'TUV',
    '9': 'WXYZ',
}

print(f"\nSequence: {sequence}")
print(f"\nT9 Keypad:")
for key, letters in t9_map.items():
    print(f"  {key}: {letters}")

# Split by * (asterisk is separator between letters)
print(f"\n{'='*70}")
print("DECODING:")
print(f"{'='*70}\n")

parts = sequence.split('*')
decoded_text = []

for i, part in enumerate(parts):
    if not part:
        continue
    
    print(f"Part {i+1}: '{part}'")
    
    # Count consecutive digits
    j = 0
    part_decoded = []
    
    while j < len(part):
        digit = part[j]
        count = 1
        
        # Count how many times this digit repeats
        while j + count < len(part) and part[j + count] == digit:
            count += 1
        
        # Get the corresponding letter
        if digit in t9_map:
            letters = t9_map[digit]
            if letters:
                letter_index = (count - 1) % len(letters)
                letter = letters[letter_index]
                part_decoded.append(letter)
                print(f"  {digit} x {count} = {letter}")
        
        j += count
    
    decoded_part = ''.join(part_decoded)
    decoded_text.append(decoded_part)
    print(f"  -> {decoded_part}\n")

# Join all parts
full_text = ''.join(decoded_text)

print(f"{'='*70}")
print(f"DECODED TEXT: {full_text}")
print(f"{'='*70}")

# Check if it's a flag
if 'CIT' in full_text.upper():
    print(f"\n✓✓ FLAG FOUND!")
    # Format properly
    flag = full_text.replace(' ', '_').lower()
    print(f"FLAG: CIT{{{flag}}}")
else:
    # Try with spaces
    spaced_text = ' '.join(decoded_text)
    print(f"\nWith spaces: {spaced_text}")
    
    # Try as flag
    flag = full_text.lower()
    print(f"\nPossible flag: CIT{{{flag}}}")

print(f"\n{'='*70}")
