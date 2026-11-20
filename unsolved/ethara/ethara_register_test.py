#!/usr/bin/env python3
"""
Test registration with proper fields
"""

import requests
import json

BASE_URL = "https://task.ethara.ai"

print("[*] Testing registration with role field...")

# Try different roles
roles = ["user", "admin", "tasker", "pl", "qr", "founder"]

for role in roles:
    print(f"\n[*] Trying role: {role}")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{role}@test.com",
            "password": "Test123!@#",
            "name": f"Test {role}",
            "role": role
        }, timeout=5)
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        
        if resp.status_code == 200 or resp.status_code == 201:
            data = resp.json()
            print(f"  [+] SUCCESS! Token: {data.get('access_token', 'N/A')[:50]}...")
            
            # Try to access protected endpoints
            if 'access_token' in data:
                token = data['access_token']
                headers = {"Authorization": f"Bearer {token}"}
                
                # Try to get flags
                print(f"\n  [*] Trying to get flags with {role} role...")
                resp2 = requests.get(f"{BASE_URL}/api/flags", headers=headers)
                print(f"    Flags endpoint: {resp2.status_code}")
                if resp2.status_code == 200:
                    print(f"    Response: {resp2.text}")
                
                # Try to get tasks
                print(f"  [*] Trying to get tasks...")
                resp3 = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
                print(f"    Tasks endpoint: {resp3.status_code}")
                if resp3.status_code == 200:
                    print(f"    Response: {resp3.text[:500]}")
                
                # Try to get user info
                print(f"  [*] Trying to get user info...")
                resp4 = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
                print(f"    Me endpoint: {resp4.status_code}")
                if resp4.status_code == 200:
                    print(f"    Response: {resp4.text}")
                
    except Exception as e:
        print(f"  Error: {e}")
