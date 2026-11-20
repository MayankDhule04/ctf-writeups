#!/usr/bin/env python3
"""
Get full source code of the page
"""

import requests

url = "http://23.179.17.92:5559"

print("="*70)
print("FULL PAGE SOURCE")
print("="*70)

r = requests.get(url, timeout=10)

# Save to file
with open('hit_your_limit_page.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f"[*] Saved to: hit_your_limit_page.html")
print(f"[*] Length: {len(r.text)} bytes")

# Extract JavaScript
import re
scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL | re.IGNORECASE)

print(f"\n[*] Found {len(scripts)} script blocks")

for i, script in enumerate(scripts):
    if script.strip() and 'FLAG' in script:
        print(f"\n[*] Script {i+1} (contains FLAG):")
        print(script)

print("\n" + "="*70)
