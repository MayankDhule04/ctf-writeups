import requests
from bs4 import BeautifulSoup
import re

TARGET = 'https://switch-ctf.tdho.st'
s = requests.Session()

# Get full HTML of register page
r = s.get(TARGET + '/register', timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')

print("=== REGISTER PAGE - ALL FORMS ===")
for f in soup.find_all('form'):
    print(f"  action={f.get('action')} method={f.get('method')}")
    for el in f.find_all(['input','select','textarea','button']):
        print(f"    {el.name}: name={el.get('name')} type={el.get('type')} value={el.get('value')} id={el.get('id')}")

# Find any hidden fields or JS that shows how form is submitted
print("\n=== ALL HIDDEN INPUTS ===")
for i in soup.find_all('input', type='hidden'):
    print(f"  {i.get('name')} = {i.get('value')}")

print("\n=== ALL SCRIPTS (inline) ===")
for sc in soup.find_all('script'):
    if sc.string:
        print(sc.string[:500])
        print("---")

# Save full HTML
with open('switch_register.html','w',encoding='utf-8') as f:
    f.write(r.text)
print("\nSaved full HTML to switch_register.html")

# Also check what actual URL / body gets used - try register with POST and GET with different params
print("\n=== TRYING DIFFERENT REGISTER APPROACHES ===")

# Try GET with form action path
for attempt in [
    ('GET', '/register', {'username': 'test99', 'password': 'test99'}),
    ('GET', '/register', {'username': 'test99', 'password': 'test99', 'role': 'admin'}),
    ('GET', '/', {'username': 'test99', 'password': 'test99'}),  # maybe form submits to /
]:
    method, path, params = attempt
    s2 = requests.Session()
    if method == 'GET':
        r2 = s2.get(TARGET + path, params=params, timeout=8, allow_redirects=True)
    else:
        r2 = s2.post(TARGET + path, data=params, timeout=8, allow_redirects=True)
    
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    body = ' '.join(soup2.get_text().split())[:200]
    cookies = dict(s2.cookies)
    print(f"{method} {path} {params} -> [{r2.status_code}] url={r2.url}")
    print(f"  Body: {body[:150]}")
    print(f"  Cookies: {cookies}")
    print()
