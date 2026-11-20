#!/usr/bin/env python3
"""
Analyze the main JavaScript file
"""

import requests
import re

BASE_URL = "https://task.ethara.ai"
JS_URL = f"{BASE_URL}/static/js/main.9bc87e42.js"

print("[*] Fetching JavaScript file...")
resp = requests.get(JS_URL)
print(f"[+] Status: {resp.status_code}")
print(f"[+] Size: {len(resp.text)} bytes")
print()

js_content = resp.text

# Look for API endpoints
print("[*] Looking for API endpoints...")
api_patterns = [
    r'["\']/(api|endpoint|task|submit|flag)[^"\']*["\']',
    r'fetch\(["\']([^"\']+)["\']',
    r'axios\.[a-z]+\(["\']([^"\']+)["\']',
]

endpoints = set()
for pattern in api_patterns:
    matches = re.findall(pattern, js_content)
    endpoints.update(matches)

if endpoints:
    print("[+] Found endpoints:")
    for ep in sorted(endpoints):
        print(f"    {ep}")
else:
    print("[-] No obvious endpoints found")

print()

# Look for flags
print("[*] Looking for flags...")
flags = re.findall(r'(CIT|FLAG|flag|CTF)\{[^}]+\}', js_content, re.IGNORECASE)
if flags:
    print(f"[+] FOUND FLAGS: {flags}")
else:
    print("[-] No flags found")

print()

# Look for interesting strings
print("[*] Looking for interesting strings...")
interesting = [
    'password', 'secret', 'key', 'token', 'admin', 'flag',
    'auth', 'login', 'api', 'endpoint'
]

for keyword in interesting:
    matches = re.findall(rf'["\'][^"\']*{keyword}[^"\']*["\']', js_content, re.IGNORECASE)
    if matches:
        print(f"\n  {keyword.upper()}:")
        for match in matches[:10]:  # Show first 10
            print(f"    {match}")

# Save the JS for manual analysis
with open('ethara_main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print(f"\n[+] JavaScript saved to ethara_main.js")

# Look for base64 encoded strings
print("\n[*] Looking for base64 encoded strings...")
b64_pattern = r'["\']([A-Za-z0-9+/]{20,}={0,2})["\']'
b64_matches = re.findall(b64_pattern, js_content)
if b64_matches:
    print(f"[+] Found {len(b64_matches)} potential base64 strings")
    import base64
    for b64 in b64_matches[:10]:
        try:
            decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
            if decoded.isprintable():
                print(f"    {b64[:50]}... -> {decoded[:100]}")
        except:
            pass
