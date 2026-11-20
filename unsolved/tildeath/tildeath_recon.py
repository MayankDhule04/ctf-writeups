#!/usr/bin/env python3
import requests, re, json

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Quick recon
paths = ['/', '/robots.txt', '/admin', '/vault', '/login', '/register',
         '/api', '/api/eulogy', '/eulogies', '/farewell', '/memorial',
         '/private', '/priest', '/sign', '/token', '/flag',
         '/.well-known', '/source', '/git']

print('[*] Recon')
for p in paths:
    try:
        r = s.get(base + p, timeout=10, allow_redirects=False)
        if r.status_code not in [404]:
            print(f'  {r.status_code} {p} ({len(r.content)}b)')
            if r.status_code == 200 and len(r.content) < 3000:
                print(f'    {r.text[:300]}')
    except Exception as e:
        print(f'  ERR {p}: {e}')

# Get main page
print('\n[*] Main page:')
r = s.get(base + '/', timeout=10)
print(r.text[:2000])
