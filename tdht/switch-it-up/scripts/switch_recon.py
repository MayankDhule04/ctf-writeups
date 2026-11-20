import requests
from bs4 import BeautifulSoup

TARGET = 'https://switch-ctf.tdho.st'
s = requests.Session()

for path in ['/', '/login', '/register', '/admin']:
    r = s.get(TARGET + path, timeout=8, allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find('title')
    title_str = title.string if title else 'N/A'
    forms = soup.find_all('form')
    print(f"{path}: [{r.status_code}] {title_str} | {len(forms)} form(s) | final_url={r.url}")
    for f in forms:
        print(f"  Form: {f.get('method','GET')} {f.get('action','')}")
        for i in f.find_all(['input','select']):
            print(f"    {i.get('name','?')} type={i.get('type','text')} value={repr(i.get('value',''))[:30]}")
    # Look for any cookies set
    print(f"  Cookies: {dict(s.cookies)}")
    body_text = soup.get_text()
    body_clean = ' '.join(body_text.split())[:300]
    print(f"  Text: {body_clean}")
    print()
