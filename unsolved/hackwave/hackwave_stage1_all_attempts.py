import requests
import json
import base64
import re

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("STAGE 1: Finding ALL Possible Fragments")
print("="*70)

session = requests.Session()

# Get /init response
r = session.get(f"{backend_url}/init")
session_token = r.headers.get('x-session-token')

print(f"[+] Session token: {session_token}\n")

# Collect ALL possible 4-character combinations
candidates = []

# 1. Direct 4-char values in headers
print("[*] 4-char header values:")
for key, value in r.headers.items():
    if len(value) == 4 and value.replace('-', '').replace('_', '').isalnum():
        print(f"  {key}: {value}")
        candidates.append(('header_direct', key, value))

# 2. First chars from different header combinations
print("\n[*] First char combinations:")

x_headers = {k: v for k, v in r.headers.items() if k.startswith('x-')}

# Try different combinations of 4 headers
important_headers = ['x-build', 'x-region', 'x-cache', 'x-via', 'x-amz-cf-id', 'x-trace-id', 'x-request-id', 'x-correlation-id']

for h1 in important_headers:
    for h2 in important_headers:
        for h3 in important_headers:
            for h4 in important_headers:
                if h1 != h2 and h1 != h3 and h1 != h4 and h2 != h3 and h2 != h4 and h3 != h4:
                    v1 = r.headers.get(h1, '')
                    v2 = r.headers.get(h2, '')
                    v3 = r.headers.get(h3, '')
                    v4 = r.headers.get(h4, '')
                    if v1 and v2 and v3 and v4:
                        combo = v1[0] + v2[0] + v3[0] + v4[0]
                        if combo.isalnum():
                            candidates.append(('first_chars', f"{h1[0]}{h2[0]}{h3[0]}{h4[0]}", combo))

# Remove duplicates
unique_candidates = {}
for type, source, value in candidates:
    if value not in unique_candidates:
        unique_candidates[value] = (type, source)

print(f"\nFound {len(unique_candidates)} unique candidates:")
for i, (value, (type, source)) in enumerate(sorted(unique_candidates.items())[:20], 1):
    print(f"  {i:2d}. {value:6s} ({type}: {source})")

# 3. Check JSON for any 4-char values
print("\n[*] 4-char values in JSON:")
data = r.json()

def find_4char_in_json(obj, path=""):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(find_4char_in_json(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_4char_in_json(item, f"{path}[{i}]"))
    elif isinstance(obj, str):
        if len(obj) == 4 and obj.isalnum():
            results.append((path, obj))
    return results

json_4chars = find_4char_in_json(data)
for path, value in json_4chars:
    print(f"  {path}: {value}")
    unique_candidates[value] = ('json', path)

# 4. Look for patterns in specific headers
print("\n[*] Analyzing specific patterns:")

# Maybe it's the last 4 chars of something?
for key in ['x-build', 'x-trace-id', 'x-request-id', 'x-correlation-id', 'x-replica-id']:
    val = r.headers.get(key, '')
    if len(val) >= 4:
        last4 = val[-4:]
        if last4.isalnum():
            print(f"  {key}[-4:]: {last4}")
            unique_candidates[last4] = ('last4', key)

# Maybe it's in the token from JSON?
token = data.get('token', '')
if len(token) >= 4:
    print(f"  token[:4]: {token[:4]}")
    print(f"  token[-4:]: {token[-4:]}")
    unique_candidates[token[:4]] = ('json_token', 'first4')
    unique_candidates[token[-4:]] = ('json_token', 'last4')

# 5. Check cookies
print("\n[*] Cookies:")
for cookie in session.cookies:
    print(f"  {cookie.name}: {cookie.value}")
    if len(cookie.value) == 4:
        unique_candidates[cookie.value] = ('cookie', cookie.name)

# 6. Maybe combine parts from different sources?
print("\n[*] Cross-source combinations:")

# Header + JSON
x_cache_first = r.headers.get('x-cache', '')[0] if r.headers.get('x-cache') else ''
x_region_first = r.headers.get('x-region', '')[0] if r.headers.get('x-region') else ''
dc = data.get('_meta', {}).get('dc', '')
region = data.get('_meta', {}).get('region', '')

if len(dc) >= 2 and x_cache_first and x_region_first:
    combo = x_cache_first + x_region_first + dc[:2]
    print(f"  x-cache[0] + x-region[0] + dc[:2]: {combo}")
    if len(combo) == 4:
        unique_candidates[combo] = ('cross', 'cache+region+dc')

print("\n" + "="*70)
print(f"TOTAL UNIQUE CANDIDATES: {len(unique_candidates)}")
print("="*70)

# Print top candidates
print("\nTop 30 candidates to try:")
for i, (value, (type, source)) in enumerate(sorted(unique_candidates.items())[:30], 1):
    print(f"  {i:2d}. {value:8s} <- {type:15s} ({source})")

print("\n[!] Most likely candidates based on challenge description:")
print("    'Fragment split across multiple locations'")
print("\n1. First chars from x-build, x-region, x-cache, x-via")
print("2. Combination of header + JSON values")
print("3. Direct 4-char header value like x-amz-cf-id")
