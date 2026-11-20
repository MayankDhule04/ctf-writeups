#!/usr/bin/env python3
import requests, re, json

base = 'https://manas-yantra-ctf1.onrender.com'
s = requests.Session()

# Get the JS to find chat endpoint
r = s.get(base + '/static/app.js', timeout=15)
print('[*] app.js:')
print(r.text[:3000])
print()

# Also check chat endpoint (POST)
r2 = s.post(base + '/chat', json={'message': 'hello'}, timeout=20)
print(f'POST /chat: {r2.status_code} -> {r2.text[:500]}')

r3 = s.post(base + '/api/chat', json={'message': 'hello'}, timeout=20)
print(f'POST /api/chat: {r3.status_code} -> {r3.text[:500]}')
