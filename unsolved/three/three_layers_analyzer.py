#!/usr/bin/env python3
"""
Three Layers Deep - Crackme Analysis
Challenge: Find valid license key for binary
"""

import struct
import re

binary_file = "ff6d46f6-187e-47ba-a7ee-c073ef4aca61_crackme"

print("="*70)
print("THREE LAYERS DEEP - CRACKME ANALYSIS")
print("="*70)
print(f"Binary: {binary_file}")
print("="*70)

# Read the binary
with open(binary_file, 'rb') as f:
    data = f.read()

print(f"\n[*] Binary size: {len(data)} bytes")

# Check ELF header
if data[:4] == b'\x7fELF':
    print("[+] Valid ELF binary")
    
    # ELF class (32 or 64 bit)
    elf_class = data[4]
    if elf_class == 1:
        print("    Architecture: 32-bit")
    elif elf_class == 2:
        print("    Architecture: 64-bit")
    
    # Endianness
    endian = data[5]
    if endian == 1:
        print("    Endianness: Little-endian")
    elif endian == 2:
        print("    Endianness: Big-endian")

# Extract printable strings (min length 4)
print("\n[*] Extracting strings...")
strings = []
current_string = b''

for byte in data:
    if 32 <= byte <= 126:  # Printable ASCII
        current_string += bytes([byte])
    else:
        if len(current_string) >= 4:
            strings.append(current_string.decode('ascii', errors='ignore'))
        current_string = b''

if len(current_string) >= 4:
    strings.append(current_string.decode('ascii', errors='ignore'))

print(f"[+] Found {len(strings)} strings")

# Save all strings
with open('three_layers_strings.txt', 'w') as f:
    for s in strings:
        f.write(s + '\n')

print("[+] Saved all strings to three_layers_strings.txt")

# Look for interesting strings
print("\n[*] Interesting strings:")

keywords = ['key', 'license', 'valid', 'correct', 'flag', 'password', 'check', 
            'verify', 'success', 'fail', 'wrong', 'invalid', 'layer', 'three']

interesting = []
for s in strings:
    s_lower = s.lower()
    if any(kw in s_lower for kw in keywords):
        interesting.append(s)
        print(f"  {s}")

# Look for potential keys (alphanumeric strings of reasonable length)
print("\n[*] Potential license keys (8-20 chars, alphanumeric):")
potential_keys = []
for s in strings:
    if 8 <= len(s) <= 20 and s.replace('_', '').replace('-', '').isalnum():
        potential_keys.append(s)
        print(f"  {s}")

# Look for function names
print("\n[*] Potential function names:")
func_pattern = re.compile(r'^[a-z_][a-z0-9_]*$', re.IGNORECASE)
for s in strings:
    if func_pattern.match(s) and len(s) > 3:
        if any(word in s.lower() for word in ['check', 'verify', 'validate', 'main', 'key', 'layer']):
            print(f"  {s}")

# Look for format strings
print("\n[*] Format strings and messages:")
for s in strings:
    if '%' in s or 'Enter' in s or 'Usage' in s or 'Error' in s:
        print(f"  {s}")

# Look for base64-like strings
print("\n[*] Potential encoded strings (base64-like):")
base64_pattern = re.compile(r'^[A-Za-z0-9+/]{16,}={0,2}$')
for s in strings:
    if base64_pattern.match(s):
        print(f"  {s}")
        # Try to decode
        try:
            import base64
            decoded = base64.b64decode(s)
            if all(32 <= b <= 126 for b in decoded):
                print(f"    -> Decodes to: {decoded.decode('ascii')}")
        except:
            pass

# Look for hex strings
print("\n[*] Potential hex strings:")
hex_pattern = re.compile(r'^[0-9a-fA-F]{16,}$')
for s in strings:
    if hex_pattern.match(s):
        print(f"  {s}")

# Search for "three" or "layer" references
print("\n[*] References to 'three' or 'layer':")
for s in strings:
    if 'three' in s.lower() or 'layer' in s.lower():
        print(f"  {s}")

# Look for comparison values
print("\n[*] Looking for magic numbers and constants...")
# Search for common patterns in the binary
magic_numbers = []
for i in range(0, len(data) - 4, 4):
    val = struct.unpack('<I', data[i:i+4])[0]
    # Look for interesting values (not too common)
    if 0x1000 < val < 0x100000:
        if data.count(data[i:i+4]) == 1:  # Unique value
            magic_numbers.append((i, val))

if magic_numbers[:10]:
    print(f"[+] Found {len(magic_numbers)} unique 4-byte values")
    print("    First 10:")
    for offset, val in magic_numbers[:10]:
        print(f"      Offset 0x{offset:x}: 0x{val:x} ({val})")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nNext steps:")
print("1. Check three_layers_strings.txt for all extracted strings")
print("2. Try potential keys found above")
print("3. Use a disassembler (Ghidra, IDA, radare2) for deeper analysis")
print("4. Look for validation logic and reverse it")
