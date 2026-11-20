#!/usr/bin/env python3
"""
Three Layers Deep - Advanced Static Analysis
Analyzes the crackme binary to find the valid license key
"""

import struct
import re
import sys

def analyze_binary(filename):
    print("="*70)
    print("THREE LAYERS DEEP - ADVANCED STATIC ANALYSIS")
    print("="*70)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"[*] Binary size: {len(data)} bytes\n")
    
    # Extract all strings
    strings = []
    current = b''
    for byte in data:
        if 32 <= byte <= 126:
            current += bytes([byte])
        else:
            if len(current) >= 4:
                strings.append(current.decode('ascii', errors='ignore'))
            current = b''
    
    # Look for the "three layers" pattern
    print("[*] Searching for 'three' or 'layer' references...")
    for s in strings:
        if 'three' in s.lower() or 'layer' in s.lower():
            print(f"  Found: {s}")
    
    # Potential keys (8-20 chars, mostly alphanumeric)
    print("\n[*] Potential license keys:")
    potential_keys = []
    for s in strings:
        if 8 <= len(s) <= 20:
            # Check if it's mostly alphanumeric
            alnum_count = sum(c.isalnum() for c in s)
            if alnum_count / len(s) > 0.7:
                potential_keys.append(s)
                print(f"  {s}")
    
    # Look for validation patterns
    print("\n[*] Looking for validation patterns...")
    
    # Search for XOR operations (common in key validation)
    xor_pattern = b'\x31'  # XOR instruction opcode
    xor_count = data.count(xor_pattern)
    print(f"  XOR instructions found: {xor_count}")
    
    # Search for CMP instructions
    cmp_pattern = b'\x3b'  # CMP instruction opcode
    cmp_count = data.count(cmp_pattern)
    print(f"  CMP instructions found: {cmp_count}")
    
    # Look for interesting constants
    print("\n[*] Interesting constants (might be used in validation):")
    
    # Common validation constants
    interesting_vals = [0x1337, 0xDEAD, 0xBEEF, 0xCAFE, 0xBABE, 0x4141, 0x5555]
    for val in interesting_vals:
        # Search for little-endian representation
        pattern = struct.pack('<I', val)
        if pattern in data:
            offset = data.find(pattern)
            print(f"  Found 0x{val:X} at offset 0x{offset:X}")
    
    # Look for base64 encoded strings
    print("\n[*] Potential base64 strings:")
    base64_pattern = re.compile(r'^[A-Za-z0-9+/]{16,}={0,2}$')
    for s in strings:
        if base64_pattern.match(s) and len(s) >= 16:
            print(f"  {s}")
            try:
                import base64
                decoded = base64.b64decode(s)
                if all(32 <= b <= 126 for b in decoded):
                    print(f"    -> {decoded.decode('ascii')}")
            except:
                pass
    
    # Analyze potential multi-layer validation
    print("\n[*] Multi-layer validation analysis:")
    print("  Challenge name suggests 3 layers of validation")
    print("  Looking for patterns that might indicate layers...")
    
    # Look for repeated validation patterns
    # Common pattern: check length, check format, check value
    validation_keywords = [b'length', b'format', b'valid', b'check', b'layer']
    for keyword in validation_keywords:
        count = data.lower().count(keyword)
        if count > 0:
            print(f"  '{keyword.decode()}' appears {count} times")
    
    return potential_keys

def try_transformations(keys):
    """Try common transformations on potential keys"""
    print("\n" + "="*70)
    print("TRYING KEY TRANSFORMATIONS")
    print("="*70)
    
    transformations = []
    
    for key in keys[:5]:  # Try first 5 keys
        # Original
        transformations.append(('original', key, key))
        
        # Reverse
        transformations.append(('reversed', key, key[::-1]))
        
        # Uppercase/lowercase
        transformations.append(('upper', key, key.upper()))
        transformations.append(('lower', key, key.lower()))
        
        # ROT13
        import codecs
        rot13 = codecs.encode(key, 'rot13')
        transformations.append(('rot13', key, rot13))
        
        # Base64
        import base64
        b64 = base64.b64encode(key.encode()).decode()
        transformations.append(('base64', key, b64))
    
    print("\n[*] Generated transformations:")
    for transform_type, original, result in transformations[:20]:
        print(f"  {transform_type:10s}: {original:15s} -> {result}")
    
    return transformations

if __name__ == "__main__":
    binary = "ff6d46f6-187e-47ba-a7ee-c073ef4aca61_crackme"
    
    try:
        keys = analyze_binary(binary)
        transformations = try_transformations(keys)
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"\nFound {len(keys)} potential keys")
        print("\nTop candidates to try:")
        for i, key in enumerate(keys[:10], 1):
            print(f"  {i:2d}. {key}")
        
        print("\n[*] To test these keys on Linux:")
        print("    1. Copy binary to Linux")
        print("    2. chmod +x ff6d46f6-187e-47ba-a7ee-c073ef4aca61_crackme")
        print("    3. echo 'KEY' | ./ff6d46f6-187e-47ba-a7ee-c073ef4aca61_crackme")
        print("\n[*] Or run the solve_crackme_on_linux.sh script")
        
    except FileNotFoundError:
        print(f"[!] Binary not found: {binary}")
        print("[!] Make sure the file is in the current directory")

