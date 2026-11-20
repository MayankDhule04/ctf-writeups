import requests
import json
import re

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

session = requests.Session()
r = session.get(f"{backend_url}/init")

print("="*70)
print("SMART ANALYSIS - Looking for SPLIT fragment")
print("="*70)

# The key word is "SPLIT" - meaning the fragment is divided
# Let's look for single chars or 2-char pieces

print("\n[*] Single-character values:")
single_chars = []

# Headers
for key, value in r.headers.items():
    if len(value) == 1:
        print(f"  Header {key}: '{value}'")
        single_chars.append(('header', key, value))

# Cookies
for cookie in session.cookies:
    if len(cookie.value) == 1:
        print(f"  Cookie {cookie.name}: '{value}'")
        single_chars.append(('cookie', cookie.name, cookie.value))

# JSON
data = r.json()

def find_single_chars(obj, path=""):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(find_single_chars(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_single_chars(item, f"{path}[{i}]"))
    elif isinstance(obj, str) and len(obj) == 1:
        results.append((path, obj))
    return results

json_singles = find_single_chars(data)
for path, value in json_singles:
    print(f"  JSON {path}: '{value}'")
    single_chars.append(('json', path, value))

# Look for 2-character values
print("\n[*] Two-character values:")
two_chars = []

for key, value in r.headers.items():
    if len(value) == 2 and value.isalnum():
        print(f"  Header {key}: '{value}'")
        two_chars.append(('header', key, value))

def find_two_chars(obj, path=""):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(find_two_chars(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_two_chars(item, f"{path}[{i}]"))
    elif isinstance(obj, str) and len(obj) == 2 and obj.isalnum():
        results.append((path, obj))
    return results

json_twos = find_two_chars(data)
for path, value in json_twos:
    print(f"  JSON {path}: '{value}'")
    two_chars.append(('json', path, value))

# Maybe it's 2+2 combination?
print("\n[*] Possible 2+2 combinations:")
if len(two_chars) >= 2:
    for i, (type1, src1, val1) in enumerate(two_chars):
        for j, (type2, src2, val2) in enumerate(two_chars):
            if i != j:
                combo = val1 + val2
                print(f"  {val1} + {val2} = {combo}")

# Look at specific locations mentioned in the hint
print("\n[*] Specific locations to check:")
print(f"  1. First header value: {list(r.headers.values())[0] if r.headers else 'N/A'}")
print(f"  2. Last header value: {list(r.headers.values())[-1] if r.headers else 'N/A'}")
print(f"  3. First cookie: {list(session.cookies)[0].value if session.cookies else 'N/A'}")
print(f"  4. JSON status: {data.get('status', 'N/A')}")
print(f"  5. JSON token (first 4): {data.get('token', '')[:4]}")
print(f"  6. JSON checksum (first 4): {data.get('checksum', '')[:4]}")

# Maybe look at the order of specific headers?
print("\n[*] Ordered header analysis:")
ordered_headers = list(r.headers.items())
print(f"  Total headers: {len(ordered_headers)}")

# Check if there are headers with 'part', 'frag', 'piece' in name
print("\n[*] Headers with fragment-related names:")
for key, value in r.headers.items():
    if any(word in key.lower() for word in ['part', 'frag', 'piece', 'chunk', 'segment']):
        print(f"  {key}: {value}")

# Check for hidden data in specific headers
print("\n[*] Analyzing x-feature-flags (base64):")
feature_flags = r.headers.get('x-feature-flags', '')
if feature_flags:
    try:
        import base64
        decoded = base64.b64decode(feature_flags).decode()
        print(f"  Encoded: {feature_flags}")
        print(f"  Decoded: {decoded}")
        
        # Parse JSON
        flags_data = json.loads(decoded)
        print(f"  Parsed: {json.dumps(flags_data, indent=4)}")
    except:
        pass

# Check correlation-id, request-id, trace-id patterns
print("\n[*] ID headers (looking for patterns):")
id_headers = ['x-correlation-id', 'x-request-id', 'x-trace-id', 'x-replica-id']
for header in id_headers:
    val = r.headers.get(header, '')
    if val:
        print(f"  {header}: {val}")
        # Check if first 4 or last 4 chars form a pattern
        if len(val) >= 4:
            print(f"    First 4: {val[:4]}")
            print(f"    Last 4: {val[-4:]}")
            # Check middle
            if len(val) >= 8:
                mid = len(val) // 2
                print(f"    Middle 4: {val[mid-2:mid+2]}")

print("\n" + "="*70)
print("BEST GUESSES:")
print("="*70)
print("\nBased on 'split across multiple locations':")
print("1. Combination of 2-char values from different sources")
print("2. Specific positions in ID headers")
print("3. Hidden in base64-encoded header")
