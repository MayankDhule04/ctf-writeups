#!/usr/bin/env python3
"""
Crackme Solution Script
Unpacks UPX-packed binary and tests potential license keys
"""

import subprocess
import os
import sys

print("="*70)
print("CRACKME SOLUTION")
print("="*70)

# Potential keys found in the binary
potential_keys = [
    'wRshe6zH',
    '9pATVihd',
    'GXMpDMUA',
    'CSRonRUjP',
    'LvFd7Scy'
]

print("\n[*] Binary is packed with UPX 4.24")
print("[*] Attempting to unpack...")

# Check if UPX is available
try:
    result = subprocess.run(['upx', '--version'], capture_output=True, text=True)
    print(f"[+] UPX found: {result.stdout.split()[0]}")
    
    # Unpack the binary
    print("[*] Unpacking crackme...")
    result = subprocess.run(['upx', '-d', 'crackme', '-o', 'crackme_unpacked'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[+] Successfully unpacked to crackme_unpacked")
        # Make it executable
        os.chmod('crackme_unpacked', 0o755)
        binary_to_test = 'crackme_unpacked'
    else:
        print(f"[-] Unpacking failed: {result.stderr}")
        print("[*] Will test with packed binary")
        binary_to_test = 'crackme'
        
except FileNotFoundError:
    print("[-] UPX not found. Install with: sudo apt install upx-ucl")
    print("[*] Will test with packed binary")
    binary_to_test = 'crackme'

# Make sure binary is executable
if os.path.exists(binary_to_test):
    os.chmod(binary_to_test, 0o755)

print(f"\n[*] Testing {len(potential_keys)} potential license keys...")
print("="*70)

# Test each key
for i, key in enumerate(potential_keys, 1):
    print(f"\n[{i}/{len(potential_keys)}] Testing key: {key}")
    print("-"*70)
    
    try:
        # Try running with the key as argument
        result = subprocess.run([f'./{binary_to_test}', key], 
                              capture_output=True, text=True, timeout=5)
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        # Check for success indicators
        success_indicators = ['correct', 'valid', 'success', 'flag', 'congratulations', 'well done']
        output_lower = (result.stdout + result.stderr).lower()
        
        if any(indicator in output_lower for indicator in success_indicators):
            print("\n" + "="*70)
            print(f"[+] POSSIBLE SUCCESS WITH KEY: {key}")
            print("="*70)
        
        # Check if return code is 0 (success)
        if result.returncode == 0:
            print(f"[+] Key '{key}' returned exit code 0 (success)")
            
    except subprocess.TimeoutExpired:
        print("[!] Timeout - binary might be waiting for input")
    except FileNotFoundError:
        print(f"[-] Binary not found or not executable")
        print("[*] Make sure you're on Linux/WSL and the binary has execute permissions")
        print("[*] Run: chmod +x crackme")
        break
    except Exception as e:
        print(f"[-] Error: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)

# Additional analysis
print("\n[*] Additional Information:")
print("  - Binary is UPX packed (version 4.24)")
print("  - Platform: Linux x86_64")
print("  - SHA-256: 4d18295080f1b21742f24b3dcb2da98d025772070aa4f8689f7b951683beb4dd")
print("\n[*] If no key worked, next steps:")
print("  1. Unpack with UPX and analyze with Ghidra/IDA")
print("  2. Look for key validation function")
print("  3. Check for dynamic key generation")
print("  4. Try running with strace/ltrace to see system calls")
print("  5. Use gdb to debug and find comparison operations")
