import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://hackwave-ctf-frontend.onrender.com"

print("="*70)
print("HACKWAVE CTF - 8 STAGE CHALLENGE SOLVER")
print("="*70)
print("Goal: Find 8 fragments (4 chars each) to build final flag")
print("Flag format: HW{...}")
print("="*70)

session = requests.Session()

# Stage 1: Initial reconnaissance
print("\n[STAGE 1] Initial Reconnaissance")
print("-"*70)

r = session.get(url)
print(f"Status: {r.status_code}")

soup = BeautifulSoup(r.text, 'html.parser')
print(f"Title: {soup.title.string if soup.title else 'N/A'}")

# Save HTML for analysis
with open('hackwave_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

# Look for fragments in HTML
print("\n[*] Searching for flag fragments in HTML...")

# Check HTML comments
comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
for comment in comments:
    print(f"  Comment: {comment.strip()}")
    if 'HW{' in comment or 'fragment' in comment.lower():
        print(f"    [!] Potential fragment found!")

# Check for hidden elements
hidden = soup.find_all(style=re.compile(r'display:\s*none'))
for elem in hidden:
    print(f"  Hidden element: {elem.get_text()[:100]}")

# Check data attributes
for tag in soup.find_all(True):
    for attr, value in tag.attrs.items():
        if 'data-' in attr or 'fragment' in attr.lower():
            print(f"  Data attribute: {tag.name}.{attr} = {value}")

# Check all text for fragments
all_text = soup.get_text()
fragments = re.findall(r'[A-Za-z0-9_]{4}', all_text)
print(f"\n[*] Found {len(set(fragments))} unique 4-char sequences")

# Look for specific patterns
hw_pattern = re.findall(r'HW\{[^}]+\}', all_text)
if hw_pattern:
    print(f"[!!!] Found complete flag: {hw_pattern}")

# Check JavaScript
print("\n[*] Analyzing JavaScript...")
scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    if script.string:
        if 'fragment' in script.string.lower() or 'HW{' in script.string:
            print(f"  Script {i} contains interesting content:")
            print(f"    {script.string[:200]}")

# Check for API endpoints
print("\n[*] Looking for API endpoints...")
links = soup.find_all('a')
for link in links:
    href = link.get('href')
    if href:
        print(f"  Link: {href}")

# Check common endpoints
endpoints = [
    '/api',
    '/stage1', '/stage2', '/stage3', '/stage4',
    '/stage5', '/stage6', '/stage7', '/stage8',
    '/fragment1', '/fragment2', '/fragment3', '/fragment4',
    '/fragment5', '/fragment6', '/fragment7', '/fragment8',
    '/robots.txt',
    '/.well-known',
    '/sitemap.xml',
]

print("\n[*] Testing common endpoints...")
for endpoint in endpoints:
    r = session.get(f"{url}{endpoint}")
    if r.status_code == 200:
        print(f"  [+] {endpoint}: {r.status_code} ({len(r.text)} bytes)")
        if len(r.text) < 500:
            print(f"      Content: {r.text[:200]}")

print("\n[*] Stage 1 reconnaissance complete!")
print("[*] Check hackwave_page.html for full HTML content")
