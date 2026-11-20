#!/usr/bin/env python3
import requests, re, json

base = 'https://manas-yantra-ctf1.onrender.com'
s = requests.Session()

# Quick recon
r = s.get(base + '/', timeout=20)
print(f'Main page: {r.status_code} ({len(r.content)}b)')
print(r.text[:2000])
print()

# Check API endpoints
for path in ['/api', '/api/chat', '/chat', '/api/message', '/message',
             '/api/v1/chat', '/kosha', '/api/kosha', '/secret',
             '/robots.txt', '/api/flag', '/flag']:
    try:
        r2 = s.get(base + path, timeout=10)
        if r2.status_code != 404:
            print(f'{r2.status_code} {path}: {r2.text[:200]}')
    except Exception as e:
        print(f'ERR {path}: {e}')
