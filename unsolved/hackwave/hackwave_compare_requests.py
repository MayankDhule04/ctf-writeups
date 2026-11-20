import requests
import json

backend_url = "https://hackwave-ctf-backend.onrender.com/api"

print("="*70)
print("COMPARING MULTIPLE /init REQUESTS")
print("="*70)
print("Looking for what CHANGES vs what STAYS THE SAME")
print("="*70)

# Make 3 requests
responses = []
for i in range(3):
    session = requests.Session()
    r = session.get(f"{backend_url}/init")
    responses.append((r, session))
    print(f"\n[Request {i+1}]")
    print(f"  Session token: {r.headers.get('x-session-token')}")
    print(f"  x-amz-cf-id: {r.headers.get('x-amz-cf-id')}")
    print(f"  x-cache: {r.headers.get('x-cache')}")
    print(f"  x-canary: {r.headers.get('x-canary')}")
    print(f"  x-build: {r.headers.get('x-build')}")
    print(f"  x-region: {r.headers.get('x-region')}")
    print(f"  x-via: {r.headers.get('x-via')}")
    print(f"  Cookie: {list(session.cookies)[0].value if session.cookies else 'None'}")
    
    data = r.json()
    print(f"  JSON token: {data.get('token')}")
    print(f"  JSON dc: {data.get('_meta', {}).get('dc')}")

# Analyze what's constant
print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

print("\n[*] Values that STAY THE SAME:")
print("  - x-amz-cf-id: Always '2e2d'")
print("  - x-region: Always 'us-east-1a'")
print("  - x-via: Always starts with '1.1'")
print("  - JSON dc: Always 'iad1'")
print("  - JSON checksum: Always same")

print("\n[*] Values that CHANGE:")
print("  - x-session-token: Different each time")
print("  - x-build: Different each time")
print("  - x-cache: Can be MISS or HIT")
print("  - x-canary: Can be true or false")
print("  - JSON token: Different each time")
print("  - Cookie: Different each time")

print("\n[*] INSIGHT:")
print("  If the fragment is 'split across multiple locations',")
print("  it's likely in the CONSTANT values, not the changing ones!")
print("\n  Constant 4-char values:")
print("    - 2e2d (x-amz-cf-id)")
print("    - iad1 (JSON _meta.dc)")
print("\n  Or maybe combining constant parts:")
print("    - First char of constant headers")
print("    - Specific positions in constant values")

# Try to find a pattern
print("\n[*] Trying combinations of constant values:")

# Get first request data
r1, s1 = responses[0]
data1 = r1.json()

# Method 1: Combine parts of constant values
amz_id = r1.headers.get('x-amz-cf-id', '')  # 2e2d
dc = data1.get('_meta', {}).get('dc', '')    # iad1
region = r1.headers.get('x-region', '')      # us-east-1a

print(f"\n  amz_id: {amz_id}")
print(f"  dc: {dc}")
print(f"  region: {region}")

# Maybe first 2 of amz + first 2 of dc?
if len(amz_id) >= 2 and len(dc) >= 2:
    combo1 = amz_id[:2] + dc[:2]
    print(f"\n  amz[:2] + dc[:2] = {combo1}")

# Maybe last 2 of amz + last 2 of dc?
if len(amz_id) >= 2 and len(dc) >= 2:
    combo2 = amz_id[-2:] + dc[-2:]
    print(f"  amz[-2:] + dc[-2:] = {combo2}")

# Maybe alternating?
if len(amz_id) >= 2 and len(dc) >= 2:
    combo3 = amz_id[0] + dc[0] + amz_id[1] + dc[1]
    print(f"  amz[0] + dc[0] + amz[1] + dc[1] = {combo3}")

# Maybe region code?
region_code = region.split('-')[1] if '-' in region else ''  # 'east'
if len(region_code) >= 4:
    print(f"  region code: {region_code[:4]}")

print("\n" + "="*70)
print("TOP CANDIDATES TO TRY (1 attempt left!):")
print("="*70)
print("1. 2eia (amz[0] + dc[0] + amz[1] + dc[1])")
print("2. 2dia (if dc is different)")
print("3. iad1 (direct from JSON)")
print("4. 2e2d (direct from header)")
