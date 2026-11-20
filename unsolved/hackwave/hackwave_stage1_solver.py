import requests
import json
import base64
import re

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("STAGE 1: Ghost Signal - Fragment Hunter")
print("="*70)

session = requests.Session()

# Get /init response
r = session.get(f"{backend_url}/init")
session_token = r.headers.get('x-session-token')

print(f"[+] Session token: {session_token}")
print("\n[*] Analyzing all data sources...")

# Method 1: Look for numbered parts (part1, part2, etc.)
print("\n--- Method 1: Numbered Parts ---")
parts_dict = {}

# Check headers
for key, value in r.headers.items():
    match = re.search(r'part[_-]?(\d+)', key, re.IGNORECASE)
    if match:
        parts_dict[int(match.group(1))] = value
        print(f"  Header {key}: {value}")

# Check cookies
for cookie in session.cookies:
    match = re.search(r'part[_-]?(\d+)', cookie.name, re.IGNORECASE)
    if match:
        parts_dict[int(match.group(1))] = cookie.value
        print(f"  Cookie {cookie.name}: {cookie.value}")

# Check JSON
data = r.json()
def find_parts(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'part' in k.lower():
                match = re.search(r'(\d+)', k)
                if match:
                    parts_dict[int(match.group(1))] = v
                    print(f"  JSON {path}.{k}: {v}")
            find_parts(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_parts(item, f"{path}[{i}]")

find_parts(data)

if parts_dict:
    assembled = ''.join([parts_dict[i] for i in sorted(parts_dict.keys())])
    print(f"\n[+] Assembled from parts: {assembled}")

# Method 2: Look for fragment in specific locations
print("\n--- Method 2: Direct Fragment References ---")

# Check for 'fragment' key in JSON
def find_fragment_keys(obj, path=""):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'fragment' in k.lower():
                results.append((f"{path}.{k}", v))
                print(f"  JSON {path}.{k}: {v}")
            results.extend(find_fragment_keys(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_fragment_keys(item, f"{path}[{i}]"))
    return results

fragments = find_fragment_keys(data)

# Check headers for fragment
for key, value in r.headers.items():
    if 'fragment' in key.lower():
        print(f"  Header {key}: {value}")
        fragments.append((key, value))

# Method 3: Decode base64 values
print("\n--- Method 3: Base64 Decoding ---")

def try_base64_decode(s):
    try:
        decoded = base64.b64decode(s).decode('utf-8', errors='ignore')
        if decoded.isprintable() and len(decoded) >= 4:
            return decoded
    except:
        pass
    return None

# Check all string values in JSON
def find_base64(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_base64(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_base64(item, f"{path}[{i}]")
    elif isinstance(obj, str) and len(obj) > 10:
        decoded = try_base64_decode(obj)
        if decoded:
            print(f"  {path}: {obj} -> {decoded}")
            # Check if decoded contains a 4-char fragment
            if len(decoded) == 4:
                print(f"    [!] Potential fragment: {decoded}")

find_base64(data)

# Method 4: First character from specific headers
print("\n--- Method 4: First Chars from Headers ---")

header_keys = ['x-build', 'x-region', 'x-cache', 'x-via']
first_chars = ''
for key in header_keys:
    val = r.headers.get(key, '')
    if val:
        first_chars += val[0]
        print(f"  {key}[0]: {val[0]}")

if len(first_chars) == 4:
    print(f"\n[+] Assembled from first chars: {first_chars}")

# Method 5: Look at specific header values
print("\n--- Method 5: Specific 4-Char Headers ---")

four_char_headers = []
for key, value in r.headers.items():
    if len(value) == 4 and value.replace('-', '').replace('_', '').isalnum():
        four_char_headers.append((key, value))
        print(f"  {key}: {value}")

# Method 6: Check if there's a pattern in header order
print("\n--- Method 6: Custom X- Headers ---")

x_headers = [(k, v) for k, v in r.headers.items() if k.startswith('x-')]
print(f"Found {len(x_headers)} X- headers")

# Look for headers with single-char or short values
for key, value in x_headers:
    if len(value) == 1:
        print(f"  {key}: '{value}' (single char)")

# Method 7: Combine specific headers
print("\n--- Method 7: Specific Header Combination ---")

# Try combining x-amz-cf-id (2e2d) with something else
# Or maybe the fragment is literally in one of these headers
candidates = [
    r.headers.get('x-amz-cf-id', ''),
    r.headers.get('x-cache', ''),
    r.headers.get('x-canary', ''),
]

print(f"Candidates: {candidates}")

# Maybe we need to look at the JSON more carefully
print("\n--- Method 8: JSON Deep Dive ---")
print(f"token: {data.get('token')}")
print(f"checksum: {data.get('checksum')}")
print(f"entropy: {data.get('data', {}).get('entropy')}")

# Decode entropy
entropy = data.get('data', {}).get('entropy', '')
if entropy:
    decoded_entropy = try_base64_decode(entropy)
    print(f"entropy decoded: {decoded_entropy}")

# Check _meta
meta = data.get('_meta', {})
print(f"_meta.dc: {meta.get('dc')}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nMost likely candidates for the 4-character fragment:")
print("1. Assembled from numbered parts (if found)")
print("2. First chars from specific headers")
print("3. One of the 4-char header values")
print("4. Decoded base64 value")
