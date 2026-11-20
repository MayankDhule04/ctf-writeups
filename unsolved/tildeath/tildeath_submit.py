#!/usr/bin/env python3
import requests, re, json, hashlib
from collections import defaultdict

base = 'http://54.210.184.191:8081'
s = requests.Session()

# The "private ledger" must be accessible somehow
# Try to POST a eulogy/farewell to see if it gets signed
# Then check if the new signature has an r-value collision with existing ones

# First check if there's a submit endpoint
print('[*] Looking for eulogy submission...')
for path in ['/eulogies', '/eulogy', '/farewell', '/farewells', '/submit', 
             '/memorial', '/api/submit', '/add', '/api/add']:
    for method in ['GET', 'POST']:
        try:
            if method == 'GET':
                r = s.get(base + path, timeout=8)
            else:
                r = s.post(base + path, json={'msg': 'test', 'name': 'test'}, timeout=8)
            if r.status_code not in [404, 405]:
                print(f'  {method} {path}: {r.status_code} -> {r.text[:150]}')
        except:
            pass

# Check the main HTML for any POST endpoints I missed
with open('tildeath_main.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# Find any forms, fetch calls, XMLHttpRequest
print('\n[*] Forms and fetch in main HTML:')
forms = re.findall(r'<form[^>]*>.*?</form>', html, re.DOTALL)
for form in forms:
    print(f'  Form: {form[:200]}')

# Find inline JS event handlers
onclick = re.findall(r'onclick=["\']([^"\']+)["\']', html)
for h in onclick:
    print(f'  onclick: {h[:100]}')

# Check the private ledger path
print('\n[*] Checking private ledger endpoints...')
paths_to_try = [
    '/ledger', '/private', '/priest/private', '/admin', '/admin/eulogies',
    '/gallery/private', '/gallery?type=private', '/priest/entries',
    '/eulogies/private', '/api/private/eulogies', '/mourner',
    '/api/mourner', '/api/gallery/private', '/entries',
]
for p in paths_to_try:
    r = s.get(base + p, timeout=8)
    if r.status_code not in [404]:
        print(f'  {r.status_code} {p}: {r.text[:200]}')
