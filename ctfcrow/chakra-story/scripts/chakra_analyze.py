#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, re, base64, json

base = 'https://gokul-hidden-makhan.vercel.app'

# Fetch and save JS
r = requests.get(base + '/assets/index-DMAKegzR.js', timeout=15)
js = r.text

# Save to file for inspection
with open('chakra_bundle.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"[*] JS size: {len(js)} chars")

# Search for CHAKRA flag
flags = re.findall(r'CHAKRA\{[^}]+\}', js)
print(f"[*] Direct flags: {flags}")

# Search for all strings that look interesting - the actual game logic
# Find the flag reveal logic
patterns = [
    r'"CHAKRA[^"]*"',
    r"'CHAKRA[^']*'",
    r'`CHAKRA[^`]*`',
    r'flag["\s:=]+["\']([^"\']+)["\']',
    r'secret["\s:=]+["\']([^"\']+)["\']',
    r'answer["\s:=]+["\']([^"\']+)["\']',
    r'correct["\s:=]+["\']([^"\']+)["\']',
]

for pat in patterns:
    matches = re.findall(pat, js, re.IGNORECASE)
    if matches:
        print(f"[+] Pattern '{pat[:30]}': {matches[:5]}")

# Find all string literals that contain flag-like content
# Look for the win condition / stage 3 logic
idx = js.find('step3')
if idx != -1:
    segment = js[max(0,idx-500):idx+1000]
    print(f"\n[*] step3 area:\n{segment}")

# Look for 'solved' or 'complete' or 'congratulations'
for kw in ['solved', 'congratul', 'correct', 'victory', 'final', 'stage3', 'step3', 'loc3']:
    idx = js.find(kw)
    if idx != -1:
        print(f"\n[*] '{kw}' at {idx}:")
        print(js[max(0,idx-200):idx+400])
        print("---")
