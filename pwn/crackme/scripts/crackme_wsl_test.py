#!/usr/bin/env python3
"""
Crackme WSL Test Script
Tests potential license keys using WSL
"""

import subprocess
import os

print("="*70)
print("CRACKME WSL TEST")
print("="*70)

# Potential keys found in the binary
potential_keys = [
    'wRshe6zH',
    '9pATVihd',
    'GXMpDMUA',
    'CSRonRUjP',
    'LvFd7Scy'
]

# Get the Windows path and convert to WSL path
windows_path = os.getcwd()
# Convert C:\Users\... to /mnt/c/Users/...
wsl_path = windows_path.replace('\\', '/').replace('C:', '/mnt/c').replace('D:', '/mnt/d')

print(f"\n[*] Windows path: {windows_path}")
print(f"[*] WSL path: {wsl_path}")

# First, make the binary executable in WSL
print("\n[*] Making binary executable...")
try:
    result = subprocess.run(['wsl', 'chmod', '+x', f'{wsl_path}/crackme'], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("[+] Binary is now executable")
    else:
        print(f"[-] chmod failed: {result.stderr}")
except Exception as e:
    print(f"[-] Error: {e}")

print(f"\n[*] Testing {len(potential_keys)} potential license keys...")
print("="*70)

# Test each key
for i, key in enumerate(potential_keys, 1):
    print(f"\n[{i}/{len(potential_keys)}] Testing key: {key}")
    print("-"*70)
    
    try:
        # Run the binary with the key as argument
        cmd = ['wsl', 'bash', '-c', f'cd {wsl_path} && ./crackme {key}']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        # Check for success indicators
        success_indicators = ['correct', 'valid', 'success', 'flag', 'congratulations', 
                            'well done', 'trx{', 'traceback{', 'ctf{']
        output_lower = (result.stdout + result.stderr).lower()
        
        if any(indicator in output_lower for indicator in success_indicators):
            print("\n" + "="*70)
            print(f"[!!!] SUCCESS WITH KEY: {key}")
            print("="*70)
        
        # Check if return code is 0 (success)
        if result.returncode == 0 and result.stdout.strip():
            print(f"[+] Key '{key}' returned exit code 0 with output")
            
    except subprocess.TimeoutExpired:
        print("[!] Timeout - binary might be waiting for input or hanging")
    except Exception as e:
        print(f"[-] Error: {e}")

print("\n" + "="*70)
print("TESTING COMPLETE")
print("="*70)

# Try running without arguments to see usage
print("\n[*] Testing binary without arguments...")
try:
    cmd = ['wsl', 'bash', '-c', f'cd {wsl_path} && ./crackme']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
except Exception as e:
    print(f"Error: {e}")

print("\n[*] Next steps if keys don't work:")
print("  1. Unpack with UPX: wsl upx -d crackme -o crackme_unpacked")
print("  2. Analyze with Ghidra or IDA Pro")
print("  3. Use ltrace: wsl ltrace ./crackme <key>")
print("  4. Use strace: wsl strace ./crackme <key>")
print("  5. Debug with gdb: wsl gdb ./crackme")
