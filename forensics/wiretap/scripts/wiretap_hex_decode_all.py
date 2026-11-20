#!/usr/bin/env python3
"""
Wiretap - Decode all hex parts separated by *
"""

# Get the full sequence from the spectral analysis
full_sequence = "AD1318A2016A3C141459521938A9A*4321539B1B17ABDA7265#5D09#8792568A14A1#92A4AB5#276C*D13*2D*40*0*040*78*7*7*7*7*8*4787*7*7*7*7*78*8070*78*7*7*7*2*0708*741*0*481*0*70*0*74*0*0*0*25*850*08*0*847*0*407080*05*74*080*5*527*0*4"

print("="*70)
print("WIRETAP - HEX DECODE ALL PARTS")
print("="*70)

# Split by *
parts = full_sequence.split('*')

print(f"\nTotal parts: {len(parts)}\n")

decoded_chars = []

for i, part in enumerate(parts):
    if not part:
        continue
    
    # Remove # characters
    clean_part = part.replace('#', '')
    
    # Check if it's valid hex
    if all(c in '0123456789ABCDEF' for c in clean_part):
        try:
            if len(clean_part) % 2 == 0 and clean_part:
                hex_bytes = bytes.fromhex(clean_part)
                text = hex_bytes.decode('ascii', errors='ignore')
                
                # Only show printable
                if all(32 <= ord(c) < 127 for c in text):
                    decoded_chars.append(text)
                    print(f"Part {i+1:3d}: {part:20s} -> {text}")
        except Exception as e:
            pass

print(f"\n{'='*70}")
print(f"DECODED MESSAGE:")
print(f"{'='*70}")

full_message = ''.join(decoded_chars)
print(f"{full_message}")

if 'CIT{' in full_message:
    print(f"\n✓✓ FLAG FOUND IN MESSAGE!")
    # Extract flag
    start = full_message.index('CIT{')
    end = full_message.index('}', start) + 1
    flag = full_message[start:end]
    print(f"FLAG: {flag}")

print(f"\n{'='*70}")
