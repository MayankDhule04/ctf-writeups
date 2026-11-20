import requests
import json
import base64
from PIL import Image
from io import BytesIO
import re

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("HACKWAVE CTF - CORRECT SOLVER")
print("="*70)

session = requests.Session()
fragments = []

# STAGE 1: Initialize and get session token
print("\n[STAGE 1] Ghost Signal - Initializing...")
print("-"*70)

r = session.get(f"{backend_url}/init")
print(f"Status: {r.status_code}")

# Extract session token from RESPONSE HEADERS (not JSON)
session_token = r.headers.get('x-session-token')
print(f"[+] Session token from headers: {session_token}")

# Now analyze the /init response for the first fragment
print("\n[*] Analyzing /init response for fragment...")
print("\n[*] All headers:")
for key, value in sorted(r.headers.items()):
    print(f"  {key}: {value}")

# The hint says "split across multiple locations"
# Let's look for patterns in headers
print("\n[*] Looking for fragment parts in headers...")

# Check for custom headers with short values
fragment_candidates = []
for key, value in r.headers.items():
    if key.startswith('x-') and len(value) == 4 and value.isalnum():
        print(f"  [!] Potential fragment: {key} = {value}")
        fragment_candidates.append((key, value))

# Check JSON response
data = r.json()
print("\n[*] JSON Response:")
print(json.dumps(data, indent=2))

# Set up headers for subsequent requests
headers = {
    'Content-Type': 'application/json',
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
    
    with open('hackwave_stage2_crypto.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage2_crypto.json")
else:
    print(f"Error: {r.text}")

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
    else:
        print(f"Response: {r.text[:200]}")
else:
    print(f"Error: {r.text}")

# STAGE 4: Networking
print("\n" + "="*70)
print("[STAGE 4] Packet Graveyard - Networking")
print("="*70)

r = session.get(f"{backend_url}/network", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1500])
    
    with open('hackwave_stage4_network.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage4_network.json")
else:
    print(f"Error: {r.text}")

# STAGE 5: Reverse Engineering
print("\n" + "="*70)
print("[STAGE 5] Phantom Code - Reverse Engineering")
print("="*70)

r = session.get(f"{backend_url}/reverse", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    print(f"Response (first 500 chars):\n{r.text[:500]}")
    
    with open('hackwave_stage5_reverse.txt', 'w') as f:
        f.write(r.text)
    print("[+] Saved to hackwave_stage5_reverse.txt")
else:
    print(f"Error: {r.text}")

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
else:
    print(f"Error: {r.text}")

# STAGE 7: Logic/Encoding
print("\n" + "="*70)
print("[STAGE 7] Scrambled Truth - Logic/Encoding")
print("="*70)

r = session.get(f"{backend_url}/order", headers=headers)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:1500])
    
    with open('hackwave_stage7_order.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("[+] Saved to hackwave_stage7_order.json")
else:
    print(f"Error: {r.text}")

print("\n" + "="*70)
print("DATA COLLECTION COMPLETE")
print("="*70)
print("All stage data collected. Now we need to solve each stage...")
