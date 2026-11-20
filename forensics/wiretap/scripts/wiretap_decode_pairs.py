#!/usr/bin/env python3
"""
Wiretap - Decode by taking pairs of hex digits
"""

sequence = "AD1318A2016A3C141459521938A9A4321539B1B17ABDA72655D098792568A14A192A4AB5276CD132D40"

print("="*70)
print("WIRETAP - DECODE HEX PAIRS")
print("="*70)

print(f"\nSequence: {sequence}")
print(f"Length: {len(sequence)}")

# Decode every 2 characters as hex
print(f"\n[1] Decoding as hex pairs:")
decoded_chars = []

for i in range(0, len(sequence)-1, 2):
    hex_pair = sequence[i:i+2]
    try:
        byte_val = int(hex_pair, 16)
        char = chr(byte_val)
        decoded_chars.append(char)
        if 32 <= byte_val < 127:
            print(f"  {hex_pair} = {byte_val:3d} = '{char}'")
        else:
            print(f"  {hex_pair} = {byte_val:3d} = [non-printable]")
    except:
        print(f"  {hex_pair} = [invalid hex]")

result = ''.join(decoded_chars)

print(f"\n{'='*70}")
print(f"DECODED TEXT:")
print(f"{'='*70}")
print(f"{result}")

# Check for flag
if 'CIT{' in result:
    print(f"\n✓✓ FLAG FOUND!")
    start = result.index('CIT{')
    end = result.index('}', start) + 1
    flag = result[start:end]
    print(f"FLAG: {flag}")
elif 'cit{' in result.lower():
    print(f"\n✓ Possible flag (case insensitive)")

print(f"\n{'='*70}")
