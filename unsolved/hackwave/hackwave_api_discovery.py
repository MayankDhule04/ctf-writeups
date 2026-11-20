import requests
import re

url = "https://hackwave-ctf-frontend.onrender.com"

print("="*70)
print("API ENDPOINT DISCOVERY")
print("="*70)

session = requests.Session()

# Read the JavaScript to find API endpoints
with open('hackwave_js_0.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Look for fetch() or axios calls
print("\n[*] Searching for API calls in JavaScript...")

# Pattern for fetch calls
fetch_pattern = r'fetch\([`"\']([^`"\']+)[`"\']'
matches = re.findall(fetch_pattern, js_content)
if matches:
    print(f"\n[+] Found {len(matches)} fetch() calls:")
    for match in set(matches):
        print(f"  {match}")

# Pattern for axios calls
axios_pattern = r'axios\.[a-z]+\([`"\']([^`"\']+)[`"\']'
matches = re.findall(axios_pattern, js_content)
if matches:
    print(f"\n[+] Found {len(matches)} axios calls:")
    for match in set(matches):
        print(f"  {match}")

# Look for /api/ patterns
api_pattern = r'[`"\']/(api/[^`"\']+)[`"\']'
matches = re.findall(api_pattern, js_content)
if matches:
    print(f"\n[+] Found {len(matches)} /api/ endpoints:")
    for match in set(matches):
        print(f"  /{match}")

# Look for endpoint definitions
endpoint_pattern = r'endpoint:[`"\']([^`"\']+)[`"\']'
matches = re.findall(endpoint_pattern, js_content)
if matches:
    print(f"\n[+] Found {len(matches)} endpoint definitions:")
    for match in set(matches):
        print(f"  {match}")

# Try common API paths
print("\n[*] Testing common API paths...")
test_paths = [
    '/api',
    '/api/init',
    '/api/crypto',
    '/api/file',
    '/api/network',
    '/api/reverse',
    '/api/osint',
    '/api/order',
    '/api/submit',
    '/api/stages',
    '/api/stage/1',
]

for path in test_paths:
    try:
        r = session.get(f"{url}{path}")
        if r.status_code != 404:
            print(f"  [+] {path}: {r.status_code} ({len(r.content)} bytes)")
            if len(r.content) < 500:
                print(f"      {r.text[:200]}")
    except Exception as e:
        print(f"  [-] {path}: Error - {e}")

# Check if there's a backend URL in the JS
print("\n[*] Looking for backend URL...")
backend_pattern = r'[`"\']https?://[^`"\']+[`"\']'
matches = re.findall(backend_pattern, js_content)
if matches:
    print(f"\n[+] Found {len(set(matches))} URLs:")
    for match in set(matches)[:20]:
        print(f"  {match}")

print("\n" + "="*70)
print("DISCOVERY COMPLETE")
print("="*70)
