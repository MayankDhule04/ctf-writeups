import requests
import json
import base64
import time

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("FINAL COMPREHENSIVE ANALYSIS")
print("="*70)
print("Waiting 90 seconds for lockout to clear...")
time.sleep(90)

session = requests.Session()
r = session.get(f"{backend_url}/init")
session_token = r.headers.get('x-session-token')

print("\n[+] Lockout cleared, analyzing fresh request...")

data = r.json()

print("\n[*] ALL CONSTANT VALUES:")
print(f"  x-amz-cf-id: {r.headers.get('x-amz-cf-id')}")
print(f"  x-region: {r.headers.get('x-region')}")
print(f"  x-via: {r.headers.get('x-via')}")
print(f"  JSON dc: {data.get('_meta', {}).get('dc')}")
print(f"  JSON region: {data.get('_meta', {}).get('region')}")
print(f"  JSON checksum: {data.get('checksum')}")
print(f"  Cookie: {list(session.cookies)[0].value if session.cookies else 'None'}")

# The hint is "split across multiple locations"
# Let's try EVERY possible way to split and combine

print("\n[*] SYSTEMATIC COMBINATIONS:")

amz = r.headers.get('x-amz-cf-id', '')  # 2e2d
dc = data.get('_meta', {}).get('dc', '')  # iad1
cookie = list(session.cookies)[0].value if session.cookies else ''  # aV85Xw
region_header = r.headers.get('x-region', '')  # us-east-1a
region_json = data.get('_meta', {}).get('region', '')  # us-east-1

print(f"\n1. Direct 4-char values:")
print(f"   - amz: {amz}")
print(f"   - dc: {dc}")
print(f"   - cookie[:4]: {cookie[:4] if len(cookie) >= 4 else 'N/A'}")
print(f"   - cookie[-4:]: {cookie[-4:] if len(cookie) >= 4 else 'N/A'}")

print(f"\n2. Combining 2+2:")
print(f"   - amz[:2] + dc[:2]: {amz[:2] + dc[:2]}")
print(f"   - amz[:2] + dc[-2:]: {amz[:2] + dc[-2:]}")
print(f"   - amz[-2:] + dc[:2]: {amz[-2:] + dc[:2]}")
print(f"   - amz[-2:] + dc[-2:]: {amz[-2:] + dc[-2:]}")
print(f"   - cookie[:2] + amz[:2]: {cookie[:2] + amz[:2] if len(cookie) >= 2 else 'N/A'}")
print(f"   - cookie[:2] + dc[:2]: {cookie[:2] + dc[:2] if len(cookie) >= 2 else 'N/A'}")

print(f"\n3. Alternating chars:")
print(f"   - amz[0] + dc[0] + amz[1] + dc[1]: {amz[0] + dc[0] + amz[1] + dc[1] if len(amz) >= 2 and len(dc) >= 2 else 'N/A'}")
print(f"   - amz[0] + dc[1] + amz[2] + dc[3]: {amz[0] + dc[1] + amz[2] + dc[3] if len(amz) >= 3 and len(dc) >= 4 else 'N/A'}")

print(f"\n4. One char from each location (header + json + cookie):")
if len(amz) >= 1 and len(dc) >= 1 and len(cookie) >= 2:
    combo1 = amz[0] + dc[0] + cookie[0] + cookie[1]
    print(f"   - amz[0] + dc[0] + cookie[0] + cookie[1]: {combo1}")
    combo2 = amz[0] + amz[1] + dc[0] + cookie[0]
    print(f"   - amz[0] + amz[1] + dc[0] + cookie[0]: {combo2}")

print(f"\n5. Specific positions in cookie:")
if len(cookie) >= 6:
    print(f"   - cookie[0,1,2,3]: {cookie[0] + cookie[1] + cookie[2] + cookie[3]}")
    print(f"   - cookie[1,2,3,4]: {cookie[1] + cookie[2] + cookie[3] + cookie[4]}")
    print(f"   - cookie[2,3,4,5]: {cookie[2] + cookie[3] + cookie[4] + cookie[5]}")
    print(f"   - cookie[0,2,4,5]: {cookie[0] + cookie[2] + cookie[4] + cookie[5]}")

print(f"\n6. Region codes:")
if '-' in region_header:
    parts = region_header.split('-')
    print(f"   - region parts: {parts}")
    if len(parts) >= 3:
        # us-east-1a -> maybe 'east'?
        print(f"   - parts[1][:4]: {parts[1][:4]}")

print(f"\n7. Checksum parts:")
checksum = data.get('checksum', '')
if len(checksum) >= 4:
    print(f"   - checksum[:4]: {checksum[:4]}")
    print(f"   - checksum[-4:]: {checksum[-4:]}")

print(f"\n8. Via header analysis:")
via = r.headers.get('x-via', '')
print(f"   - via: {via}")
# 1.1 Mzc=.cloudfront.net
# Maybe decode Mzc=?
if '=' in via:
    encoded_part = via.split()[1] if len(via.split()) > 1 else ''
    if encoded_part:
        try:
            decoded = base64.b64decode(encoded_part).decode()
            print(f"   - via base64 part '{encoded_part}' decodes to: {decoded}")
        except:
            pass

print("\n" + "="*70)
print("MOST LIKELY CANDIDATES (in order of probability):")
print("="*70)

candidates = [
    ("2eia", "amz[:2] + dc[:2]"),
    ("2iea", "alternating: amz[0] + dc[0] + amz[1] + dc[1]"),
    ("aV85", "cookie[:4]"),
    ("85Xw", "cookie[-4:]"),
    ("2iad", "amz[0] + dc"),
    ("2ea1", "amz[0] + amz[1] + dc[1] + dc[3]"),
]

for i, (value, description) in enumerate(candidates, 1):
    print(f"{i}. {value:6s} <- {description}")

print("\n[!] Ready to test. Recommend trying in this order.")
