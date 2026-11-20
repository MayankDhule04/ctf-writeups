#!/usr/bin/env python3
import requests, re, json, hashlib, time
from collections import defaultdict

base = 'http://54.210.184.191:8081'
s = requests.Session()

# Get full gallery - try different params  
print('[*] Fetching full gallery...')
r = s.get(base + '/gallery', timeout=15)
gallery = r.json()['gallery']
print(f'  Regular: {len(gallery)} entries')

# Try to get more
for param in ['?all=true', '?limit=1000', '?page=0', '?private=1']:
    r2 = s.get(base + '/gallery' + param, timeout=15)
    if r2.status_code == 200:
        g2 = r2.json().get('gallery', [])
        if len(g2) > len(gallery):
            print(f'  With {param}: {len(g2)} entries!')
            gallery = g2

# Check for separate priest/private endpoint
for path in ['/priest/gallery', '/priest/ledger', '/private', '/ledger', '/priest']:
    r3 = s.get(base + path, timeout=10)
    if r3.status_code == 200:
        print(f'  {path}: {r3.text[:200]}')

print(f'\n[*] Analyzing {len(gallery)} signatures for nonce reuse...')

# Check r-value collisions
r_map = defaultdict(list)
for e in gallery:
    r_map[e['r']].append(e)

collisions = {r: es for r, es in r_map.items() if len(es) >= 2}
print(f'[*] R-value collisions: {len(collisions)}')

if collisions:
    for r_val, entries in collisions.items():
        print(f'\nCOLLISION at r={r_val}:')
        for e in entries:
            print(f'  msg={e["msg"][:60]}')
            print(f'  s={e["s"]}')
        
        # Recover private key using ECDSA nonce reuse
        # For ECDSA: s = k^-1 * (z + r*d) mod n
        # With two messages using same k: s1*k = z1 + r*d, s2*k = z2 + r*d
        # (s1 - s2)*k = z1 - z2 mod n
        # k = (z1 - z2) * (s1 - s2)^-1 mod n
        # Then d = (s1*k - z1) * r^-1 mod n
        
        # SECP256R1 (P-256) order
        n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
        
        e1, e2 = entries[0], entries[1]
        msg1 = e1['msg'].encode()
        msg2 = e2['msg'].encode()
        
        # Hash the messages (SHA-256)
        z1 = int(hashlib.sha256(msg1).hexdigest(), 16)
        z2 = int(hashlib.sha256(msg2).hexdigest(), 16)
        
        s1 = int(e1['s'], 16)
        s2 = int(e2['s'], 16)
        r_int = int(e1['r'], 16)
        
        # Recover k
        k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
        print(f'\nRecovered k: 0x{k:x}')
        
        # Recover private key d
        d = ((s1 * k - z1) * pow(r_int, -1, n)) % n
        print(f'Recovered d (private key): 0x{d:x}')
        
        # Verify d
        # Sign a test message and verify
        if d > 0 and d < n:
            print(f'[+] Private key recovered!')
            
            # Now forge a signature for the vault
            import time
            unix_time = int(time.time())
            # Round to current minute start
            unix_time_min = unix_time - (unix_time % 60)
            
            msg_vow = f'i remember you at {unix_time}'.encode()
            z_vow = int(hashlib.sha256(msg_vow).hexdigest(), 16)
            
            # Sign with recovered key
            # Use a deterministic k (RFC 6979 style) or simple approach
            # Simple: use k from the collision
            r_new = r_int  # reuse same r (same k)
            s_new = (pow(k, -1, n) * (z_vow + r_new * d)) % n
            
            print(f'\n[*] Forged signature for vault:')
            print(f'msg: {msg_vow.decode()}')
            print(f'r: 0x{r_new:x}')
            print(f's: 0x{s_new:x}')
            
            # Submit to vault
            payload = {
                'msg': msg_vow.decode(),
                'r': hex(r_new),
                's': hex(s_new)
            }
            print(f'\n[*] Submitting to vault...')
            rv = s.post(base + '/vault/reunion', json=payload, timeout=15)
            print(f'Status: {rv.status_code}')
            print(f'Response: {rv.text}')
            
            # Try a few more timestamps
            for offset in range(-60, 60, 10):
                ts = unix_time + offset
                msg_try = f'i remember you at {ts}'.encode()
                z_try = int(hashlib.sha256(msg_try).hexdigest(), 16)
                s_try = (pow(k, -1, n) * (z_try + r_int * d)) % n
                rv2 = s.post(base + '/vault/reunion', 
                             json={'msg': msg_try.decode(), 'r': hex(r_int), 's': hex(s_try)},
                             timeout=10)
                if rv2.status_code == 200:
                    print(f'[+] SUCCESS at ts={ts}!')
                    print(rv2.text)
                    break
                elif rv2.status_code not in [403]:
                    print(f'  ts={ts}: {rv2.status_code} {rv2.text[:80]}')
