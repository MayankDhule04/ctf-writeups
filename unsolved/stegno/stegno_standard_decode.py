#!/usr/bin/env python3
"""
Standard Zero-Width Steganography Decoder
Based on common implementations like stegzero.com and zwsp-steg-js

Common encoding: Binary using ZWNJ (0) and ZWJ (1), with BOM as delimiter/padding
"""

file_path = "cit_stegno.txt"

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

ZWNJ = '\u200C'  # Zero Width Non-Joiner
ZWJ = '\u200D'   # Zero Width Joiner  
BOM = '\uFEFF'   # Zero Width No-Break Space

print("="*70)
print("STANDARD ZERO-WIDTH STEGANOGRAPHY DECODER")
print("="*70)

# Extract all zero-width characters
zw_chars = [c for c in text if c in [ZWNJ, ZWJ, BOM]]
print(f"\n[*] Found {len(zw_chars)} zero-width characters")

# Method 1: Standard binary (ZWNJ=0, ZWJ=1, ignore BOM)
print("\n[*] Method 1: Binary (ZWNJ=0, ZWJ=1, ignore BOM)")
binary = ''.join('0' if c == ZWNJ else '1' if c == ZWJ else '' for c in zw_chars)
print(f"    Binary length: {len(binary)} bits")
print(f"    Binary: {binary[:80]}...")

decoded = ''
for i in range(0, len(binary), 8):
    byte = binary[i:i+8]
    if len(byte) == 8:
        try:
            char_code = int(byte, 2)
            if char_code > 0:  # Skip nulls
                decoded += chr(char_code)
        except:
            pass

print(f"    Decoded: {decoded}")
if 'CIT{' in decoded:
    print(f"\n[!!!] FLAG FOUND: {decoded}")

# Method 2: Binary with BOM as byte separator
print("\n[*] Method 2: BOM as byte separator")
# Split by BOM
parts = []
current = []
for c in zw_chars:
    if c == BOM:
        if current:
            parts.append(current)
            current = []
    else:
        current.append(c)
if current:
    parts.append(current)

print(f"    Found {len(parts)} parts")
decoded2 = ''
for part in parts:
    binary = ''.join('0' if c == ZWNJ else '1' for c in part)
    if binary:
        try:
            char_code = int(binary, 2)
            if 32 <= char_code <= 126:
                decoded2 += chr(char_code)
        except:
            pass

print(f"    Decoded: {decoded2}")
if 'CIT{' in decoded2:
    print(f"\n[!!!] FLAG FOUND: {decoded2}")

# Method 3: Reverse binary (ZWJ=0, ZWNJ=1)
print("\n[*] Method 3: Reverse binary (ZWJ=0, ZWNJ=1, ignore BOM)")
binary_rev = ''.join('1' if c == ZWNJ else '0' if c == ZWJ else '' for c in zw_chars)

decoded3 = ''
for i in range(0, len(binary_rev), 8):
    byte = binary_rev[i:i+8]
    if len(byte) == 8:
        try:
            char_code = int(byte, 2)
            if char_code > 0:
                decoded3 += chr(char_code)
        except:
            pass

print(f"    Decoded: {decoded3}")
if 'CIT{' in decoded3:
    print(f"\n[!!!] FLAG FOUND: {decoded3}")

# Method 4: UTF-8 multi-byte handling
print("\n[*] Method 4: UTF-8 byte sequence")
binary_clean = ''.join('0' if c == ZWNJ else '1' if c == ZWJ else '' for c in zw_chars)

# Try to decode as UTF-8 bytes
try:
    byte_array = []
    for i in range(0, len(binary_clean), 8):
        byte = binary_clean[i:i+8]
        if len(byte) == 8:
            byte_array.append(int(byte, 2))
    
    decoded4 = bytes(byte_array).decode('utf-8', errors='ignore')
    print(f"    Decoded (UTF-8): {decoded4}")
    if 'CIT{' in decoded4:
        print(f"\n[!!!] FLAG FOUND: {decoded4}")
except Exception as e:
    print(f"    Error: {e}")

# Method 5: Show raw hex
print("\n[*] Method 5: Raw hex bytes")
binary_clean = ''.join('0' if c == ZWNJ else '1' if c == ZWJ else '' for c in zw_chars)
hex_bytes = []
for i in range(0, min(len(binary_clean), 160), 8):
    byte = binary_clean[i:i+8]
    if len(byte) == 8:
        hex_bytes.append(f"{int(byte, 2):02x}")

print(f"    First 20 bytes (hex): {' '.join(hex_bytes[:20])}")

# Try ASCII interpretation
ascii_str = ''
for hex_byte in hex_bytes:
    val = int(hex_byte, 16)
    if 32 <= val <= 126:
        ascii_str += chr(val)
    else:
        ascii_str += '.'

print(f"    ASCII: {ascii_str[:50]}")

print("\n" + "="*70)
