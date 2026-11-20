#!/usr/bin/env python3
import requests, re, json, hashlib
from collections import defaultdict

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Get all gallery signatures
r = s.get(base + '/gallery', timeout=15)
gallery = r.json()['gallery']

print(f'[*] Got {len(gallery)} gallery entries')

# Find entries with same r value (same nonce k = nonce reuse)
r_to_entries = defaultdict(list)
for entry in gallery:
    r_val = int(entry['r'], 16)
    r_to_entries[r_val].append(entry)

print('[*] Checking for nonce reuse (same r value)...')
collisions = {r: entries for r, entries in r_to_entries.items() if len(entries) >= 2}
print(f'[*] Found {len(collisions)} r-value collisions!')

for r_val, entries in collisions.items():
    print(f'\nCollision at r=0x{r_val:x}:')
    for e in entries:
        print(f'  idx={e["idx"]}: {e["msg"][:60]}')
        print(f'    r=0x{int(e["r"],16):x}')
        print(f'    s=0x{int(e["s"],16):x}')

# Check vault/reunion endpoint
print('\n[*] Checking /vault/reunion...')
r_vault = s.get(base + '/vault/reunion', timeout=10)
print(f'Status: {r_vault.status_code}')
print(r_vault.text[:500])

# Also POST
r_vault2 = s.post(base + '/vault/reunion', json={}, timeout=10)
print(f'POST Status: {r_vault2.status_code}')
print(r_vault2.text[:500])
