import requests
import re
import json
import base64
from PIL import Image
from io import BytesIO
import time

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("HACKWAVE CTF - FINAL SOLVER")
print("="*70)
print(f"Backend: {backend_url}")
print("="*70)

session = requests.Session()
fragments = []

# First, call /init to start the timer and get any initial data
print("\n[INIT] Starting challenge...")
print("-"*70)

try:
    r = session.get(f"{backend_url}/init")
    print(f"Status: {r.status_code}")
    
    # Check headers for fragments
    print("\n[*] Headers:")
    for key, value in r.headers.items():
        print(f"  {key}: {value}")
    
    # Check cookies
    print("\n[*] Cookies:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")
    
    # Check body
    try:
        data = r.json()
        print("\n[*] Response JSON:")
        print(json.dumps(data, indent=2))
    except:
        print(f"\n[*] Response text: {r.text}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 1: Ghost Signal - /init endpoint
# Fragment split across headers, cookies, etc.
print("\n" + "="*70)
print("[STAGE 1] Ghost Signal - Web/Recon")
print("="*70)
print("Hint: Fragment split across multiple locations in HTTP response")

try:
    r = session.get(f"{backend_url}/init")
    
    # Collect all potential fragment parts
    fragment_parts = []
    
    # Check custom headers (X- headers often contain data)
    for key, value in r.headers.items():
        if key.startswith('X-') and len(value) <= 4:
            print(f"  [!] Custom header {key}: {value}")
            fragment_parts.append((key, value))
    
    # Check cookies
    for cookie in session.cookies:
        if len(cookie.value) <= 4 and cookie.value.isalnum():
            print(f"  [!] Cookie {cookie.name}: {cookie.value}")
            fragment_parts.append((cookie.name, cookie.value))
    
    # Check JSON response
    try:
        data = r.json()
        if 'fragment' in data:
            print(f"  [!] JSON fragment: {data['fragment']}")
            fragment_parts.append(('json', data['fragment']))
        if 'part1' in data or 'part2' in data:
            parts = [data.get(f'part{i}', '') for i in range(1, 5)]
            assembled = ''.join(parts)
            print(f"  [!] Assembled from parts: {assembled}")
            fragment_parts.append(('assembled', assembled))
    except:
        pass
    
    print(f"\n[*] Found {len(fragment_parts)} potential fragment parts")
    for name, value in fragment_parts:
        print(f"    {name}: {value}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 2: Cipher Labyrinth - /crypto endpoint
print("\n" + "="*70)
print("[STAGE 2] Cipher Labyrinth - Crypto")
print("="*70)
print("Hint: Seven layers of encoding, keys hidden in response")

try:
    r = session.get(f"{backend_url}/crypto")
    print(f"Status: {r.status_code}")
    
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 3: Dead Pixels - /file endpoint
print("\n" + "="*70)
print("[STAGE 3] Dead Pixels - Forensics")
print("="*70)
print("Hint: PNG file, LSB steganography in pixel data")

try:
    r = session.get(f"{backend_url}/file")
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Content-Length: {len(r.content)} bytes")
    
    if 'image' in r.headers.get('Content-Type', ''):
        with open('hackwave_stage3.png', 'wb') as f:
            f.write(r.content)
        print("[+] Saved image to hackwave_stage3.png")
        
        # Analyze image
        img = Image.open(BytesIO(r.content))
        print(f"[*] Image size: {img.size}")
        print(f"[*] Image mode: {img.mode}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 4: Packet Graveyard - /network endpoint
print("\n" + "="*70)
print("[STAGE 4] Packet Graveyard - Networking")
print("="*70)
print("Hint: ICMP packets, data in TTL field")

try:
    r = session.get(f"{backend_url}/network")
    print(f"Status: {r.status_code}")
    
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 5: Phantom Code - /reverse endpoint
print("\n" + "="*70)
print("[STAGE 5] Phantom Code - Reverse Engineering")
print("="*70)
print("Hint: Obfuscated JavaScript, trust nothing")

try:
    r = session.get(f"{backend_url}/reverse")
    print(f"Status: {r.status_code}")
    print(f"Response (first 500 chars):\n{r.text[:500]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 6: Shadow Profile - /osint endpoint
print("\n" + "="*70)
print("[STAGE 6] Shadow Profile - OSINT")
print("="*70)
print("Hint: Public sources, Caesar cipher")

try:
    r = session.get(f"{backend_url}/osint")
    print(f"Status: {r.status_code}")
    
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 7: Scrambled Truth - /order endpoint
print("\n" + "="*70)
print("[STAGE 7] Scrambled Truth - Logic/Encoding")
print("="*70)
print("Hint: Encoded stream + candidates, one is real")

try:
    r = session.get(f"{backend_url}/order")
    print(f"Status: {r.status_code}")
    
    data = r.json()
    print(json.dumps(data, indent=2)[:1000])
    
except Exception as e:
    print(f"[-] Error: {e}")

print("\n" + "="*70)
print("RECONNAISSANCE COMPLETE")
print("="*70)
print("Now analyzing responses to extract fragments...")
