import requests
import json

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("SUBMITTING STAGE 1 ANSWER")
print("="*70)

session = requests.Session()

# Initialize
r = session.get(f"{backend_url}/init")
session_token = r.headers.get('x-session-token')

print(f"[+] Session token: {session_token}")

# Extract the fragment from first chars
x_build = r.headers.get('x-build', '')
x_region = r.headers.get('x-region', '')
x_cache = r.headers.get('x-cache', '')
x_via = r.headers.get('x-via', '')

fragment = x_build[0] + x_region[0] + x_cache[0] + x_via[0]

print(f"\n[*] Extracted fragment: {fragment}")
print(f"  x-build[0]: {x_build[0]}")
print(f"  x-region[0]: {x_region[0]}")
print(f"  x-cache[0]: {x_cache[0]}")
print(f"  x-via[0]: {x_via[0]}")

# Submit to /verify endpoint
headers = {
    'Content-Type': 'application/json',
    'x-session-token': session_token
}

payload = {
    'stage': 1,
    'answer': fragment
}

print(f"\n[*] Submitting to /verify...")
print(f"Payload: {json.dumps(payload)}")

r = session.post(f"{backend_url}/verify", headers=headers, json=payload)

print(f"\nStatus: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    data = r.json()
    print(f"\n[+] SUCCESS!")
    print(json.dumps(data, indent=2))
    
    # Now try to access Stage 2
    print("\n[*] Attempting to access Stage 2...")
    r2 = session.get(f"{backend_url}/crypto", headers=headers)
    print(f"Stage 2 Status: {r2.status_code}")
    if r2.status_code == 200:
        print("[+] Stage 2 is now unlocked!")
        print(f"Response (first 500 chars):\n{r2.text[:500]}")
else:
    print(f"\n[-] Failed. Response: {r.text}")
