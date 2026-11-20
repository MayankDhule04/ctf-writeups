#!/usr/bin/env python3
"""
Crackme Binary Analyzer
Reverse engineering tool to find the valid license key
"""

import os
import subprocess
import re

print("="*70)
print("CRACKME BINARY ANALYZER")
print("="*70)

# Check if binary exists
if not os.path.exists('crackme'):
    print("[-] Binary 'crackme' not found!")
    exit(1)

# Get file info
file_size = os.path.getsize('crackme')
print(f"\n[*] File: crackme")
print(f"[*] Size: {file_size} bytes")

# Read binary content
with open('crackme', 'rb') as f:
    binary_data = f.read()

print(f"[*] Binary data length: {len(binary_data)} bytes")

# Check ELF header
if binary_data[:4] == b'\x7fELF':
    print("[+] ELF binary detected")
    
    # Check architecture
    if binary_data[4] == 2:
        print("[+] Architecture: 64-bit")
    elif binary_data[4] == 1:
        print("[+] Architecture: 32-bit")
else:
    print("[-] Not an ELF binary")

# Extract strings from binary
print("\n[*] Extracting strings from binary...")
strings = []
current_string = b''

for byte in binary_data:
    if 32 <= byte <= 126:  # Printable ASCII
        current_string += bytes([byte])
    else:
        if len(current_string) >= 4:  # Minimum string length
            try:
                strings.append(current_string.decode('ascii'))
            except:
                pass
        current_string = b''

# Add last string if any
if len(current_string) >= 4:
    try:
        strings.append(current_string.decode('ascii'))
    except:
        pass

print(f"[+] Found {len(strings)} strings")

# Look for interesting strings
print("\n[*] Interesting strings:")
keywords = ['key', 'license', 'valid', 'correct', 'flag', 'password', 'check', 'success', 'fail', 'error', 'enter', 'input']

interesting = []
for s in strings:
    s_lower = s.lower()
    if any(kw in s_lower for kw in keywords):
        interesting.append(s)
        print(f"  {s}")

# Look for potential keys (alphanumeric strings of reasonable length)
print("\n[*] Potential license keys (alphanumeric strings 8-32 chars):")
potential_keys = []
for s in strings:
    if 8 <= len(s) <= 32 and s.replace('-', '').replace('_', '').isalnum():
        potential_keys.append(s)
        print(f"  {s}")

# Save all strings to file
with open('crackme_strings.txt', 'w', encoding='utf-8') as f:
    for s in strings:
        f.write(s + '\n')

print(f"\n[+] All strings saved to crackme_strings.txt")

# Look for common patterns
print("\n[*] Looking for common patterns...")

# Check for base64-like strings
base64_pattern = re.compile(r'[A-Za-z0-9+/]{16,}={0,2}')
for s in strings:
    if base64_pattern.match(s):
        print(f"  Base64-like: {s}")

# Check for hex strings
hex_pattern = re.compile(r'^[0-9a-fA-F]{16,}$')
for s in strings:
    if hex_pattern.match(s):
        print(f"  Hex-like: {s}")

# Check for UUID/GUID patterns
uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
for s in strings:
    if uuid_pattern.match(s):
        print(f"  UUID-like: {s}")

print("\n[*] Analysis complete!")
print("\n[*] Next steps:")
print("  1. Try running the binary (if on Linux): ./crackme")
print("  2. Use a disassembler (Ghidra, IDA, radare2)")
print("  3. Try the potential keys found above")
print("  4. Look for validation logic in the binary")
