#!/usr/bin/env python3
import requests, re, json

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Check the full main page for vault/reunion
with open('tildeath_main.html', 'r', encoding='utf-8', errors='replace') as f:
    main = f.read()

# Find vault/reunion context
idx = main.find('/vault/reunion')
if idx != -1:
    print('vault/reunion context:')
    print(main[max(0,idx-300):idx+500])
print()

# Check all entries - maybe there's a private ledger endpoint
print('[*] Testing more endpoints...')
for path in ['/ledger', '/private/ledger', '/priest/ledger', '/priest/private',
             '/priest/farewells', '/priest/eulogies', '/private/eulogies',
             '/api/private', '/api/ledger', '/farewells', '/all',
             '/gallery/all', '/gallery?private=true', '/gallery?admin=1']:
    r = s.get(base + path, timeout=10, allow_redirects=False)
    if r.status_code not in [404, 301, 302]:
        print(f'  {r.status_code} {path}: {r.text[:200]}')

# Try POST to vault/reunion with different payloads
print('\n[*] Testing vault/reunion POST formats...')
payloads = [
    {'token': 'test'},
    {'signature': 'test', 'message': 'test'},
    {'vow': 'test'},
    {'r': '0x1', 's': '0x1', 'msg': 'test'},
    {'reunion': 'true'},
]
for payload in payloads:
    r = s.post(base + '/vault/reunion', json=payload, timeout=10)
    print(f'  {json.dumps(payload)}: {r.status_code} -> {r.text[:100]}')

# Also try main page again - look for hidden forms or JS
print('\n[*] Looking for inline JS...')
scripts = re.findall(r'<script[^>]*>(.*?)</script>', main, re.DOTALL)
for sc in scripts:
    if sc.strip():
        print(f'Script: {sc[:500]}')

# Look for data-* attributes
data_attrs = re.findall(r'data-[a-z-]+=["\'](.*?)["\']', main)
for d in data_attrs:
    print(f'data attr: {d[:100]}')

# Look for base64-encoded content
b64 = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', main)
for b in b64[:5]:
    print(f'B64 candidate: {b[:60]}')
