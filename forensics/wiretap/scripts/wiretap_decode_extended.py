#!/usr/bin/env python3
"""
Wiretap - Decode Extended DTMF
The sequence contains 0-9, A-D, *, #
"""

# First part of the sequence before it gets repetitive
sequence = "AD1318A2016A3C141459521938A9A*4321539B1B17ABDA7265#5D09#8792568A14A1#92A4AB5#276C*D13*2D*40"

print("="*70)
print("WIRETAP - EXTENDED DTMF DECODER")
print("="*70)

print(f"\nSequence: {sequence}")
print(f"Length: {len(sequence)}")

# Try as hex
print(f"\n[1] Interpreting as hexadecimal:")
try:
    # Remove * and # which aren't hex
    hex_part = sequence.replace('*', '').replace('#', '')
    print(f"  Hex string: {hex_part}")
    
    # Try to decode
    if len(hex_part) % 2 == 0:
        hex_bytes = bytes.fromhex(hex_part)
        text = hex_bytes.decode('ascii', errors='ignore')
        print(f"  Decoded: {text}")
        if 'CIT{' in text or 'cit{' in text.lower():
            print(f"  ✓✓ FOUND FLAG: {text}")
except Exception as e:
    print(f"  Error: {e}")

# Try treating * as separator and # as something else
print(f"\n[2] Using * as separator:")
parts = sequence.split('*')
for i, part in enumerate(parts[:10]):  # First 10 parts
    print(f"  Part {i+1}: {part}")
    
    # Try as hex
    if all(c in '0123456789ABCDEF' for c in part.replace('#', '')):
        try:
            hex_clean = part.replace('#', '')
            if len(hex_clean) % 2 == 0 and hex_clean:
                hex_bytes = bytes.fromhex(hex_clean)
                text = hex_bytes.decode('ascii', errors='ignore')
                if text.isprintable():
                    print(f"    -> {text}")
        except:
            pass

# Try treating the whole thing as hex (ignoring separators)
print(f"\n[3] Full hex decode (removing separators):")
try:
    clean_hex = sequence.replace('*', '').replace('#', '')
    if len(clean_hex) % 2 == 0:
        result_bytes = bytes.fromhex(clean_hex)
        result_text = result_bytes.decode('ascii', errors='ignore')
        print(f"  {result_text}")
        
        if 'CIT{' in result_text:
            print(f"\n  ✓✓ FLAG FOUND: {result_text}")
except Exception as e:
    print(f"  Error: {e}")

# Maybe A-D are special characters or modifiers
print(f"\n[4] Treating A-D as special:")
print(f"  A could be: 10 or special char")
print(f"  B could be: 11 or special char")
print(f"  C could be: 12 or special char")
print(f"  D could be: 13 or special char")

# Try replacing A-D with values
replacements = {
    'A': '10', 'B': '11', 'C': '12', 'D': '13'
}

expanded = sequence
for old, new in replacements.items():
    expanded = expanded.replace(old, new)

print(f"\n  Expanded: {expanded[:100]}...")

print(f"\n{'='*70}")
