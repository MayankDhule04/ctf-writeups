#!/usr/bin/env python3
import requests, re, json, hashlib
from collections import defaultdict

base = 'http://54.210.184.191:8081'
s = requests.Session()

# The challenge says "every mourner may leave an eulogy"
# and "every goodbye in the public gallery carries his hand"
# So we can SUBMIT a eulogy and it gets SIGNED by the priest
# Then we look for a collision between our signed eulogy's r value and existing ones

# Find the eulogy submission endpoint
# The challenge mentions "leave an eulogy" - look for POST /eulogy or similar
print('[*] Trying to submit a eulogy...')

# Try all typical endpoints for submitting
endpoints = [
    ('/eulogy', 'POST', {'msg': 'in loving memory of Test'}),
    ('/eulogies', 'POST', {'msg': 'in loving memory of Test'}),
    ('/farewell', 'POST', {'msg': 'in loving memory of Test'}),
    ('/farewells', 'POST', {'msg': 'in loving memory of Test'}),
    ('/gallery', 'POST', {'msg': 'in loving memory of Test'}),
    ('/mourn', 'POST', {'msg': 'in loving memory of Test'}),
    ('/memorial', 'POST', {'msg': 'in loving memory of Test'}),
    ('/remember', 'POST', {'msg': 'in loving memory of Test'}),
    ('/sign', 'POST', {'msg': 'in loving memory of Test'}),
    ('/priest/sign', 'POST', {'msg': 'in loving memory of Test'}),
    ('/api/eulogy', 'POST', {'msg': 'in loving memory of Test'}),
    ('/api/eulogies', 'POST', {'msg': 'in loving memory of Test'}),
    ('/api/sign', 'POST', {'msg': 'in loving memory of Test'}),
]

for path, method, payload in endpoints:
    try:
        r = s.request(method, base + path, json=payload, timeout=8)
        if r.status_code not in [404, 405]:
            print(f'  {method} {path}: {r.status_code} -> {r.text[:300]}')
    except Exception as e:
        pass

# Also try GET versions
for path in ['/mourn', '/mourner', '/leave', '/add', '/submit']:
    r = s.get(base + path, timeout=5)
    if r.status_code not in [404]:
        print(f'  GET {path}: {r.status_code} -> {r.text[:100]}')

# Look at the main page more carefully - maybe there's a form hidden in the HTML
# Let me get the raw main page HTML and look at ALL elements
print('\n[*] Checking main page for form/interaction elements...')
r = s.get(base + '/', timeout=10)

# Find input elements, buttons, data attributes
inputs = re.findall(r'<input[^>]*>', r.text)
for inp in inputs:
    print(f'  Input: {inp}')

buttons = re.findall(r'<button[^>]*>.*?</button>', r.text, re.DOTALL)
for btn in buttons:
    print(f'  Button: {btn[:100]}')

# Find script tags with JavaScript
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', r.text)
print(f'  External scripts: {scripts}')

# Find any hinted URL patterns
# "every mourner may leave an eulogy" - the endpoint is for mourners
# Let me try the specific word "mourn"
for path in ['/mourn', '/mourner', '/mourners', '/leave-eulogy', '/add-eulogy',
             '/post-eulogy', '/new-eulogy', '/submit-eulogy']:
    try:
        r2 = s.post(base + path, json={'msg': 'test'}, timeout=5)
        if r2.status_code not in [404, 405]:
            print(f'  POST {path}: {r2.status_code} -> {r2.text[:200]}')
    except:
        pass
