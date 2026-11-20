import requests
import re
import json
import base64
from PIL import Image
from io import BytesIO

url = "https://hackwave-ctf-frontend.onrender.com"

print("="*70)
print("HACKWAVE CTF - COMPLETE SOLVER")
print("="*70)
print("8 Stages - 4 fragments to collect")
print("="*70)

session = requests.Session()
fragments = []

# STAGE 1: Ghost Signal - Web/Recon
# "Inspect HTTP response - headers, cookies, everything"
print("\n[STAGE 1] Ghost Signal - Web/Recon")
print("-"*70)
print("Description: Fragment split across headers, cookies, etc.")

try:
    r = session.get(f"{url}/init")
    print(f"Status: {r.status_code}")
    
    # Check all headers
    print("\n[*] Response Headers:")
    fragment_parts = []
    for key, value in r.headers.items():
        print(f"  {key}: {value}")
        # Look for fragment hints
        if 'fragment' in key.lower() or 'flag' in key.lower() or 'x-' in key.lower():
            print(f"    [!] Potential fragment part: {value}")
            fragment_parts.append(value)
    
    # Check cookies
    print("\n[*] Cookies:")
    for cookie in session.cookies:
        print(f"  {cookie.name}: {cookie.value}")
        if 'fragment' in cookie.name.lower() or 'flag' in cookie.name.lower():
            print(f"    [!] Potential fragment part: {cookie.value}")
            fragment_parts.append(cookie.value)
    
    # Check response body
    print("\n[*] Response Body:")
    try:
        data = r.json()
        print(json.dumps(data, indent=2))
        
        # Look for fragment in JSON
        if 'fragment' in data:
            print(f"  [!] Fragment in JSON: {data['fragment']}")
            fragment_parts.append(data['fragment'])
    except:
        print(f"  Body (first 200 chars): {r.text[:200]}")
    
    # Assemble fragment
    if fragment_parts:
        stage1_fragment = ''.join(fragment_parts)
        print(f"\n[+] Stage 1 Fragment: {stage1_fragment}")
        fragments.append(stage1_fragment)
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 2: Cipher Labyrinth - Crypto
# "Seven layers of encoding. Keys hidden in response."
print("\n[STAGE 2] Cipher Labyrinth - Crypto")
print("-"*70)
print("Description: Seven layers of encoding, keys in response")

try:
    r = session.get(f"{url}/crypto")
    print(f"Status: {r.status_code}")
    
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:500])
        
        # Look for encoded data and keys
        if 'encoded' in data or 'cipher' in data or 'data' in data:
            print("\n[*] Found encoded data, attempting to decode...")
            # This will need custom logic based on the actual response
            
    except:
        print(f"Body: {r.text[:300]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 3: Dead Pixels - Forensics
# "PNG file. Fragment in pixel data LSB"
print("\n[STAGE 3] Dead Pixels - Forensics")
print("-"*70)
print("Description: PNG file, LSB steganography")

try:
    r = session.get(f"{url}/file")
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    
    if 'image' in r.headers.get('Content-Type', ''):
        # Save image
        with open('hackwave_stage3.png', 'wb') as f:
            f.write(r.content)
        print("[+] Saved image to hackwave_stage3.png")
        
        # Try LSB extraction
        img = Image.open(BytesIO(r.content))
        pixels = list(img.getdata())
        
        # Extract LSB from red channel
        bits = []
        for pixel in pixels[:1000]:  # Check first 1000 pixels
            if isinstance(pixel, tuple):
                bits.append(str(pixel[0] & 1))
        
        # Convert bits to text
        bit_string = ''.join(bits)
        chars = []
        for i in range(0, len(bit_string), 8):
            byte = bit_string[i:i+8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        
        text = ''.join(chars)
        print(f"[*] LSB extracted text (first 100 chars): {text[:100]}")
        
        # Look for 4-char fragment
        fragment_match = re.search(r'[A-Za-z0-9_]{4}', text)
        if fragment_match:
            print(f"[+] Potential fragment: {fragment_match.group()}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 4: Packet Graveyard - Networking
# "ICMP packets, data in TTL field"
print("\n[STAGE 4] Packet Graveyard - Networking")
print("-"*70)
print("Description: ICMP packets, TTL field contains data")

try:
    r = session.get(f"{url}/network")
    print(f"Status: {r.status_code}")
    
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:500])
        
        # Look for packet data with TTL
        if 'packets' in data:
            ttls = []
            for packet in data['packets']:
                if 'ttl' in packet:
                    ttls.append(packet['ttl'])
            
            print(f"[*] TTL values: {ttls}")
            # Convert TTL to chars
            fragment = ''.join([chr(t) for t in ttls if 32 <= t <= 126])
            print(f"[+] Fragment from TTL: {fragment}")
            
    except:
        print(f"Body: {r.text[:300]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 5: Phantom Code - Reverse Engineering
# "Obfuscated JavaScript. Some paths lead nowhere."
print("\n[STAGE 5] Phantom Code - Reverse Engineering")
print("-"*70)
print("Description: Obfuscated JS, trust nothing")

try:
    r = session.get(f"{url}/reverse")
    print(f"Status: {r.status_code}")
    print(f"Body (first 300 chars): {r.text[:300]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 6: Shadow Profile - OSINT
# "Intelligence from public sources. Shift cipher."
print("\n[STAGE 6] Shadow Profile - OSINT")
print("-"*70)
print("Description: OSINT with Caesar cipher")

try:
    r = session.get(f"{url}/osint")
    print(f"Status: {r.status_code}")
    
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:500])
    except:
        print(f"Body: {r.text[:300]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

# STAGE 7: Scrambled Truth - Logic/Encoding
# "Two paths. Long encoded stream and candidates."
print("\n[STAGE 7] Scrambled Truth - Logic/Encoding")
print("-"*70)
print("Description: Encoded stream + candidates, one is real")

try:
    r = session.get(f"{url}/order")
    print(f"Status: {r.status_code}")
    
    try:
        data = r.json()
        print(json.dumps(data, indent=2)[:500])
    except:
        print(f"Body: {r.text[:300]}")
    
except Exception as e:
    print(f"[-] Error: {e}")

print("\n" + "="*70)
print("INITIAL RECONNAISSANCE COMPLETE")
print("="*70)
print(f"Fragments collected: {len(fragments)}")
for i, frag in enumerate(fragments, 1):
    print(f"  Fragment {i}: {frag}")
