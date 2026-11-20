#!/usr/bin/env python3
import requests, re, json

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Get priest's public key
print('[*] /priest/pubkey.pem')
r = s.get(base + '/priest/pubkey.pem', timeout=10)
print(r.status_code)
print(r.text)
print()

# Get gallery
print('[*] /gallery')
r2 = s.get(base + '/gallery', timeout=10)
print(f'Status: {r2.status_code}, Size: {len(r2.content)}')
print(r2.text[:3000])
print()

# Save gallery
with open('tildeath_gallery.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(r2.text)

# Look for more endpoints in main page
with open('tildeath_main.html', 'r', encoding='utf-8', errors='replace') as f:
    main = f.read()

# Find all API paths
api_paths = re.findall(r'["\'/](?:api|priest|vault|admin|private|eulogy|farewell|sign|memorial)[^"\'<>]*', main)
print('API paths in main:', set(api_paths))

# Find any tokens/signatures in main page
# The "public gallery" carries "his hand, signed and sealed"
# Each eulogy is SIGNED by the priest
sigs = re.findall(r'(?:sig|sign|token|jwt|hash)["\s:=]+["\']([^"\']+)["\']', main, re.IGNORECASE)
print('Signatures:', sigs[:5])
