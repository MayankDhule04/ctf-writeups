#!/usr/bin/env python3
import os, re, base64, struct, zlib

folder = r'c:\Users\mayan\OneDrive\Desktop\ctf\challenge\challenge\evidence'

print("="*60)
print("FRAGMENT ANALYSIS")
print("="*60)

# === Fragment 03 (disk image) ===
print("\n[FRAGMENT 03 - fragment_03.dd]")
with open(os.path.join(folder, 'fragment_03.dd'), 'rb') as f:
    data = f.read()
# Search for strings
strings = re.findall(rb'[A-Za-z0-9_{}()\[\]@#$%^&*!?:;.,/\\\-=+| ]{5,}', data)
for s in strings[:50]:
    dec = s.decode('latin-1')
    if any(kw in dec.upper() for kw in ['CHAKRA','CTF','FLAG','FRAG','VAULT','KEY','SECRET','PASS']):
        print(f"  STRING: {dec}")
# Also search for CHAKRA pattern
chakra = re.findall(rb'CHAKRA\{[^}]+\}', data)
for c in chakra:
    print(f"  CHAKRA FLAG: {c}")

# === Browser artifact (SQLite) ===
print("\n[FRAGMENT 05 - browser_artifact.bin]")
with open(os.path.join(folder, 'browser_artifact.bin'), 'rb') as f:
    data = f.read()
print(data.decode('utf-8', errors='replace'))

# === Spider eye PNG - extract all tEXt/metadata ===
print("\n[FRAGMENT 06 - spider_eye.png]")
with open(os.path.join(folder, 'spider_eye.png'), 'rb') as f:
    data = f.read()

# Parse PNG chunks
pos = 8  # skip PNG signature
chunks = []
while pos < len(data):
    if pos + 8 > len(data):
        break
    length = struct.unpack('>I', data[pos:pos+4])[0]
    chunk_type = data[pos+4:pos+8].decode('ascii', errors='replace')
    chunk_data = data[pos+8:pos+8+length]
    crc = data[pos+8+length:pos+12+length]
    chunks.append((chunk_type, chunk_data))
    pos += 12 + length

for ctype, cdata in chunks:
    if ctype in ['tEXt', 'iTXt', 'zTXt']:
        print(f"  PNG chunk {ctype}: {cdata.decode('latin-1', errors='replace')[:200]}")
    elif ctype == 'IDAT':
        print(f"  IDAT chunk: {len(cdata)} bytes")
    elif ctype not in ['IHDR', 'IEND']:
        print(f"  Chunk {ctype}: {cdata[:50]}")

# Look for CHAKRA in PNG
chakra = re.findall(rb'CHAKRA\{[^}]+\}', data)
for c in chakra:
    print(f"  FLAG: {c}")

# === Network traffic ===
print("\n[FRAGMENT 07 - chakra_traffic.pcapng]")
with open(os.path.join(folder, 'chakra_traffic.pcapng'), 'rb') as f:
    data = f.read()
# Find all readable strings
strings = re.findall(rb'[A-Za-z0-9_{}:;.,\-=+/\\ ]{4,}', data)
for s in strings:
    dec = s.decode('latin-1')
    if any(kw in dec.upper() for kw in ['CHAKRA','CTF','FLAG','FRAG','VAULT','KEY','SECRET','HTTP']):
        print(f"  STRING: {dec}")
chakra = re.findall(rb'CHAKRA\{[^}]+\}', data)
for c in chakra:
    print(f"  FLAG: {c}")

# === 7z archive ===
print("\n[FRAGMENT 08 - damaged_archive.7z]")
with open(os.path.join(folder, 'damaged_archive.7z'), 'rb') as f:
    data = f.read()
print(data.decode('utf-8', errors='replace')[:500])
chakra = re.findall(rb'CHAKRA\{[^}]+\}', data)
for c in chakra:
    print(f"  FLAG: {c}")

# === Memory dump ===
print("\n[FRAGMENT 01 - chakra_memory.raw]")
with open(os.path.join(folder, 'chakra_memory.raw'), 'rb') as f:
    data = f.read()
chakra = re.findall(rb'CHAKRA\{[^}]+\}', data)
for c in chakra:
    print(f"  FLAG: {c}")
strings = re.findall(rb'[A-Za-z0-9_{}:;.,\-=+/\\ ]{6,}', data)
for s in strings:
    dec = s.decode('latin-1')
    if any(kw in dec.upper() for kw in ['CHAKRA','CTF','FLAG','FRAG','VAULT','KEY','SPIDER','BROKEN']):
        print(f"  STRING: {dec}")

print("\n[CHECKSUMS]")
with open(os.path.join(folder, '..', 'checksums.sha256'), 'rb') as f:
    print(f.read().decode('utf-8', errors='replace'))
