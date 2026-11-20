#!/usr/bin/env python3
"""
Final theory on the secret:
q355q636678723p4 means:
1. Use key=q355 to get the SVG
2. Extract data at positions: 636, 678, 723, 4
3. The 'p' might mean "positions" or "pattern"
"""
import xml.etree.ElementTree as ET

print("[*] SIGNAL - SECRET DECODE FINAL")
print("="*70)

secret = "q355q636678723p4"
print(f"Secret: {secret}")

# Parse: q355 | q636678723 | p4
# Interpretation: key=q355, then look at k=636,678,723,4

print("\n[Theory]")
print("  q355 = use this as the key parameter")
print("  636678723 = look at data-k values: 636, 678, 723")
print("  p4 = look at data-k value: 4")

# Load the q355 SVG
tree = ET.parse('signal_q355.svg')
root = tree.getroot()
rects = root.findall('.//{http://www.w3.org/2000/svg}rect')

# Create k_map
k_map = {}
for rect in rects:
    k = int(rect.get('data-k', '0'))
    if k not in k_map:
        k_map[k] = []
    k_map[k].append(rect)

# Extract at specific positions
target_positions = [636, 678, 723, 4]

print(f"\n[*] Extracting from signal_q355.svg at positions: {target_positions}")

for pos in target_positions:
    if pos in k_map:
        for rect in k_map[pos]:
            fill = rect.get('fill', '')
            cls = rect.get('class', '')
            x = rect.get('x', '')
            y = rect.get('y', '')
            print(f"  k={pos}: class={cls:8s} fill={fill:10s} x={x:6s} y={y:6s}")

# Maybe we need to look at ALL positions from 4 to 723?
print("\n[*] Alternative: Extract range from k=4 to k=723")

range_rects = []
for k in range(4, 724):
    if k in k_map:
        for rect in k_map[k]:
            if rect.get('class') == 'bit':  # Only signal bits
                range_rects.append({
                    'k': k,
                    'fill': rect.get('fill')
                })

print(f"Found {len(range_rects)} 'bit' rectangles in range 4-723")

if len(range_rects) > 0:
    # Sort by k
    range_rects.sort(key=lambda r: r['k'])
    
    # Try different color mappings
    for green_color in ['#00ff00', '#00f000']:
        for blue_color in ['#0000ff', '#0000dd']:
            
            binary_str = ''
            for rect in range_rects:
                fill = rect['fill']
                if fill == green_color:
                    binary_str += '1'
                elif fill == blue_color:
                    binary_str += '0'
                else:
                    # Other colors - try both
                    if fill in ['#00ff00', '#00f000']:
                        binary_str += '1'
                    else:
                        binary_str += '0'
            
            # Decode
            ascii_chars = []
            for i in range(0, len(binary_str), 8):
                chunk = binary_str[i:i+8]
                if len(chunk) == 8:
                    byte_val = int(chunk, 2)
                    if 32 <= byte_val <= 126:
                        ascii_chars.append(chr(byte_val))
                    else:
                        ascii_chars.append('.')
            
            ascii_text = ''.join(ascii_chars)
            
            if 'Kaal{' in ascii_text:
                print(f"\n*** FOUND FLAG! ***")
                print(f"Green={green_color}, Blue={blue_color}")
                print(ascii_text)
                
                # Extract flag
                start = ascii_text.index('Kaal{')
                end = ascii_text.index('}', start) + 1
                flag = ascii_text[start:end]
                print(f"\nFLAG: {flag}")
                exit(0)

# Maybe the numbers are telling us something else?
# 636, 678, 723 - what's the pattern?
# 678 - 636 = 42
# 723 - 678 = 45

print("\n[*] Analyzing number pattern:")
print(f"  636, 678, 723")
print(f"  Differences: {678-636}, {723-678}")
print(f"  Maybe these are byte positions in the binary stream?")

# Try extracting bytes at these positions
all_bits = []
for k in sorted(k_map.keys()):
    if k in k_map:
        for rect in k_map[k]:
            if rect.get('class') == 'bit':
                fill = rect.get('fill')
                if fill in ['#00ff00', '#00f000']:
                    all_bits.append('1')
                else:
                    all_bits.append('0')

binary_str = ''.join(all_bits)
print(f"\nTotal bits: {len(binary_str)}")

# Extract bytes at positions 636, 678, 723, 4
byte_positions = [4, 636, 678, 723]
extracted_bytes = []

for byte_pos in byte_positions:
    bit_start = byte_pos * 8
    bit_end = bit_start + 8
    
    if bit_end <= len(binary_str):
        byte_bits = binary_str[bit_start:bit_end]
        byte_val = int(byte_bits, 2)
        char = chr(byte_val) if 32 <= byte_val <= 126 else '.'
        extracted_bytes.append(char)
        print(f"  Byte {byte_pos}: {byte_bits} = {byte_val} = '{char}'")

extracted_text = ''.join(extracted_bytes)
print(f"\nExtracted: {extracted_text}")

print("\n" + "="*70)
