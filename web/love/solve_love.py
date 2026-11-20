#!/usr/bin/env python3
"""
Complete solution - try everything
"""

import requests
import base64
import hashlib
from datetime import datetime
import pytz

BASE_URL = "https://love-pagal-haiiiiiii.onrender.com"

def decode_flag_all_methods():
    """Try all possible decoding methods"""
    print("=" * 60)
    print("TRYING ALL DECODING METHODS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/flag", timeout=10)
        flag_data = response.json()['flag']
        
        # Method 1: Maybe the flag IS the encoded data itself with a pattern
        print(f"\n[*] Method 1: Check if encoded data contains flag")
        if 'TRACE' in flag_data:
            print(f"[+] Found TRACE in encoded data!")
        
        # Method 2: Decode and concatenate everything
        parts = flag_data.split('||')
        full_decoded = ''
        for part in parts:
            try:
                decoded = base64.b32decode(part).decode('utf-8', errors='ignore')
                full_decoded += decoded
            except:
                pass
        
        print(f"\n[*] Method 2: Full decoded length: {len(full_decoded)}")
        if 'TRACECTF{' in full_decoded:
            start = full_decoded.find('TRACECTF{')
            end = full_decoded.find('}', start) + 1
            flag = full_decoded[start:end]
            print(f"[+] FOUND FLAG: {flag}")
            return flag
        
        # Method 3: The hint said "Look deeper into the source of time"
        # Maybe we need to access it at 2PM IST?
        print(f"\n[*] Method 3: Time-based hint analysis")
        print(f"    Hint: 'Look deeper into the source of time'")
        print(f"    This might mean we need to access during 2PM-2:30PM IST window")
        
        # Method 4: Maybe the flag is simply displayed differently
        # Let's check the raw response
        print(f"\n[*] Method 4: Checking raw response")
        raw_response = requests.get(f"{BASE_URL}/api/flag", timeout=10)
        print(f"    Status: {raw_response.status_code}")
        print(f"    Headers: {dict(raw_response.headers)}")
        
        # Check if flag is in headers
        for key, value in raw_response.headers.items():
            if 'flag' in key.lower() or 'TRACE' in value:
                print(f"[+] Found in header {key}: {value}")
        
        # Method 5: Try the /api/confess endpoint with POST and correct time
        print(f"\n[*] Method 5: Trying /api/confess with simulated 2PM time")
        
        # Simulate 2PM IST
        headers_2pm = {
            'x-love-time': '14:00:00',
            'x-love-token': 'love',
            'x-love-proof': 'simple',
            'x-love-signature': hashlib.md5(b'love').hexdigest()
        }
        
        try:
            resp = requests.post(f"{BASE_URL}/api/confess", headers=headers_2pm, timeout=5)
            print(f"    POST Status: {resp.status_code}")
            print(f"    Response: {resp.text}")
            
            if resp.status_code == 200 and 'TRACE' in resp.text:
                return resp.text
        except Exception as e:
            print(f"    Error: {e}")
        
        # Method 6: Check if there's a pattern in the base32 itself
        print(f"\n[*] Method 6: Analyzing base32 pattern")
        # Take first character of each base32 part
        first_chars = ''.join([p[0] if p else '' for p in parts])
        print(f"    First chars of base32: {first_chars}")
        
        if 'TRACE' in first_chars:
            print(f"[+] Found TRACE in first characters!")
    
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def main():
    flag = decode_flag_all_methods()
    
    if flag:
        print(f"\n" + "=" * 60)
        print(f"FINAL FLAG: {flag}")
        print("=" * 60)
    else:
        print(f"\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("\nKey Findings:")
        print("1. /api/flag returns base32 encoded data split by ||")
        print("2. Hint: 'Look deeper into the source of time'")
        print("3. Challenge window: 2PM-2:30PM IST")
        print("4. /api/confess requires POST with headers:")
        print("   - x-love-time")
        print("   - x-love-token")
        print("   - x-love-proof")
        print("   - x-love-signature")
        print("\nThe flag might only be accessible during the 2PM-2:30PM IST window!")

if __name__ == "__main__":
    main()
