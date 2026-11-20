import requests
import re
import json
import base64
from PIL import Image
from io import BytesIO

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("HACKWAVE CTF - SESSION-BASED SOLVER")
print("="*70)

session = requests.Session()
fragments = {}

# STAGE 1: Initialize and extract fragment from /init
print("\n[STAGE 1] Ghost Signal - Initializing...")
print("-"*70)

r = session.get(f"{backend_url}/init")
print(f"Status: {r.status_code}")

# Extract session token
session_token = r.headers.get('x-session-token')
print(f"[+] Session token: {session_token}")

# Store all headers for analysis
print("\n[*] Analyzing all headers for fragment parts...")
header_parts = []

# Look at all X- headers
for key, value in r.headers.items():
    if key.startswith('x-') and len(value) <= 10:
        print(f"  {key}: {value}")
        # Check if it's a 4-char alphanumeric
        if len(value) == 4 and value.replace('_', '').isalnum():
            header_parts.append(value)

# Parse JSON response
data = r.json()
print("\n[*] JSON Response:")
print(json.dumps(data, indent=2))

# Look for fragment in JSON - check all string values
print("\n[*] Checking JSON for 4-char strings...")
def check_json_recursive(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_json_recursive(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_json_recursive(item, f"{path}[{i}]")
    elif isinstance(obj, str):
        if len(obj) == 4 and obj.replace('_', '').isalnum():
            print(f"  {path}: {obj}")

check_json_recursive(data)

# The hint says "split across multiple locations"
# Let's try to assemble from different parts
print("\n[*] Attempting to assemble fragment from multiple sources...")

# Try combining first char from different headers
assembly_attempts = []

# Method 1: First char of specific headers
attempt1 = ""
for header in ['x-build', 'x-region', 'x-cache', 'x-via']:
    val = r.headers.get(header, '')
    if val:
        attempt1 += val[0]
print(f"  Method 1 (first chars): {attempt1}")

# Method 2: Look for numbered parts in headers
parts = {}
for key, value in r.headers.items():
    match = re.search(r'part[_-]?(\d+)', key, re.IGNORECASE)
    if match:
        parts[int(match.group(1))] = value

if parts:
    assembled = ''.join([parts[i] for i in sorted(parts.keys())])
    print(f"  Method 2 (numbered parts): {assembled}")

# Method 3: Check if any header value is exactly 4 chars
for key, value in r.headers.items():
    if len(value) == 4 and value.isalnum():
        print(f"  Method 3 (4-char header): {key} = {value}")

# Now set up headers for subsequent requests
headers = {
    'x-session-token': session_token
}

# STAGE 2: Crypto
print("\n" + "="*70)
print("[STAGE 2] Cipher Labyrinth - Crypto")
print("="*70)

r = session.get(f"{backend_url}/crypto", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
    
    # Save for detailed analysis
    with open('hackwave_stage2_crypto.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage2_crypto.json")

# STAGE 3: Forensics
print("\n" + "="*70)
print("[STAGE 3] Dead Pixels - Forensics")
print("="*70)

r = session.get(f"{backend_url}/file", headers=headers)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")

if r.status_code == 200:
    if 'image' in r.headers.get('Content-Type', ''):
        with open('hackwave_stage3.png', 'wb') as f:
            f.write(r.content)
        print(f"[+] Saved image ({len(r.content)} bytes)")
        
        img = Image.open(BytesIO(r.content))
        print(f"[*] Image: {img.size}, mode: {img.mode}")

# STAGE 4: Networking
print("\n" + "="*70)
print("[STAGE 4] Packet Graveyard - Networking")
print("="*70)

r = session.get(f"{backend_url}/network", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
    with open('hackwave_stage4_network.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage4_network.json")

# STAGE 5: Reverse Engineering
print("\n" + "="*70)
print("[STAGE 5] Phantom Code - Reverse Engineering")
print("="*70)

r = session.get(f"{backend_url}/reverse", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    print(f"Response:\n{r.text[:500]}")
    
    with open('hackwave_stage5_reverse.txt', 'w') as f:
        f.write(r.text)
    print("[+] Saved to hackwave_stage5_reverse.txt")

# STAGE 6: OSINT
print("\n" + "="*70)
print("[STAGE 6] Shadow Profile - OSINT")
print("="*70)

r = session.get(f"{backend_url}/osint", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2))
    
    with open('hackwave_stage6_osint.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage6_osint.json")

# STAGE 7: Logic/Encoding
print("\n" + "="*70)
print("[STAGE 7] Scrambled Truth - Logic/Encoding")
print("="*70)

r = session.get(f"{backend_url}/order", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
    with open('hackwave_stage7_order.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage7_order.json")

print("\n" + "="*70)
print("DATA COLLECTION COMPLETE")
print("="*70)
print("All stage data saved. Now analyzing...")
