import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://hackwave-ctf-frontend.onrender.com"

print("="*70)
print("HACKWAVE CTF - DEEP ANALYSIS")
print("="*70)

session = requests.Session()

# Get main page
r = session.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

# Extract JavaScript and CSS URLs
js_files = []
css_files = []

for script in soup.find_all('script', src=True):
    js_url = script['src']
    if not js_url.startswith('http'):
        js_url = url + js_url
    js_files.append(js_url)

for link in soup.find_all('link', rel='stylesheet'):
    if link.get('href'):
        css_url = link['href']
        if not css_url.startswith('http'):
            css_url = url + css_url
        css_files.append(css_url)

print(f"\n[*] Found {len(js_files)} JavaScript files")
print(f"[*] Found {len(css_files)} CSS files")

# Download and analyze JavaScript
fragments_found = []

for i, js_url in enumerate(js_files):
    print(f"\n[*] Analyzing JavaScript file {i+1}: {js_url}")
    try:
        r = session.get(js_url)
        js_content = r.text
        
        # Save for manual inspection
        with open(f'hackwave_js_{i}.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"    Size: {len(js_content)} bytes")
        
        # Look for fragments
        if 'fragment' in js_content.lower():
            print("    [!] Contains 'fragment' keyword")
            matches = re.findall(r'fragment["\']?\s*[:=]\s*["\']([^"\']+)["\']', js_content, re.IGNORECASE)
            for match in matches:
                print(f"        Fragment: {match}")
                fragments_found.append(match)
        
        # Look for HW{ pattern
        hw_matches = re.findall(r'HW\{[^}]+\}', js_content)
        if hw_matches:
            print(f"    [!!!] Found complete flag: {hw_matches}")
        
        # Look for stage references
        stage_matches = re.findall(r'stage["\']?\s*[:=]\s*["\']?(\d+)', js_content, re.IGNORECASE)
        if stage_matches:
            print(f"    Stages referenced: {set(stage_matches)}")
        
        # Look for API endpoints
        api_matches = re.findall(r'["\']/(api|stage|fragment)[^"\']*["\']', js_content)
        if api_matches:
            print(f"    API endpoints: {set(api_matches)[:10]}")
        
        # Look for 4-character strings that might be fragments
        potential_fragments = re.findall(r'["\']([A-Za-z0-9_]{4})["\']', js_content)
        if len(potential_fragments) > 0:
            unique_frags = list(set(potential_fragments))[:20]
            print(f"    Potential 4-char fragments: {unique_frags}")
        
    except Exception as e:
        print(f"    Error: {e}")

# Download and analyze CSS
for i, css_url in enumerate(css_files):
    print(f"\n[*] Analyzing CSS file {i+1}: {css_url}")
    try:
        r = session.get(css_url)
        css_content = r.text
        
        with open(f'hackwave_css_{i}.css', 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"    Size: {len(css_content)} bytes")
        
        # Look for fragments in CSS (sometimes hidden in content properties)
        if 'fragment' in css_content.lower() or 'HW{' in css_content:
            print("    [!] Contains interesting content")
            
    except Exception as e:
        print(f"    Error: {e}")

# Try to access the app and see what loads
print("\n[*] Checking for dynamically loaded content...")
print("[*] Trying to access with headers that might reveal more...")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html',
}

r = session.get(url, headers=headers)
print(f"Response size: {len(r.text)} bytes")

# Check cookies
if session.cookies:
    print(f"\n[*] Cookies set: {dict(session.cookies)}")

# Check response headers
print(f"\n[*] Response headers:")
for key, value in r.headers.items():
    if 'flag' in key.lower() or 'fragment' in key.lower() or 'stage' in key.lower():
        print(f"    {key}: {value}")

print("\n[*] Analysis complete!")
print(f"[*] Fragments found: {fragments_found}")
print("[*] Check saved JS and CSS files for manual inspection")
