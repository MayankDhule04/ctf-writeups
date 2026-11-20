#!/usr/bin/env python3
import requests, re

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Get full page and look for all endpoints/tokens
r = s.get(base + '/', timeout=15)

# Save full page
with open('tildeath_main.html', 'w', encoding='utf-8', errors='replace') as f:
    f.write(r.text)

# Find all URLs/endpoints
endpoints = re.findall(r'(?:href|src|action|fetch|url)[="\s]+["\']?(/[^"\'>\s]+)', r.text)
print('Endpoints found:', set(endpoints))

# Find JS files
js_files = re.findall(r'src=["\']([^"\']+\.js)["\']', r.text)
print('JS files:', js_files)

# Find any API calls
api_calls = re.findall(r'(?:fetch|axios|xhr|post|get)\s*\(["\']([^"\']+)["\']', r.text)
print('API calls:', api_calls)

# Find any tokens/hashes/signatures
tokens = re.findall(r'[A-Za-z0-9+/=]{32,}', r.text)
print('Long tokens:')
for t in tokens[:10]:
    print(f'  {t[:80]}')

# Look for form actions
forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\']', r.text)
print('Forms:', forms)

# Flags
flags = re.findall(r'CHAKRA\{[^}]+\}', r.text)
print('Flags found:', flags)

# Check source for JS
print('\n[*] Checking static files...')
for path in ['/static/app.js', '/static/main.js', '/static/memorial.js', 
             '/static/style.css', '/app.js', '/main.js']:
    try:
        r2 = s.get(base + path, timeout=10)
        if r2.status_code == 200:
            print(f'  Found: {path} ({len(r2.content)}b)')
            print(f'  Content: {r2.text[:500]}')
    except:
        pass

# Check more paths
print('\n[*] More paths...')
for p in ['/api/eulogies', '/api/farewells', '/api/sign', '/eulogy', 
          '/farewells', '/api/vault', '/vault/flag', '/api/flag',
          '/submit', '/api/submit', '/api/private']:
    try:
        r3 = s.get(base + p, timeout=10, allow_redirects=False)
        if r3.status_code not in [404]:
            print(f'  {r3.status_code} {p}: {r3.text[:200]}')
    except:
        pass
