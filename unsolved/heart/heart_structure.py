#!/usr/bin/env python3
"""
Understand the heart.dmp structure.
The file is 109424 = 0x1AB70 bytes.
Header says HEARTLIST=0x555555458000, image_base=0x555555400000
0x555555458000 - 0x555555400000 = 0x58000 which is > file size.

So it's NOT a flat memory dump. It must be a structured custom format.
Let's read the full header carefully to find the node layout.
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
print(f'Dump size: {size} = 0x{size:x}')

# Print bytes 0x00 to 0x600 in readable format
print('\n=== HEADER REGION (first 0x600 bytes) ===')
i = 0
while i < min(0x600, size):
    b = raw[i]
    if b == 0x0a:  # newline
        print()
        i += 1
    elif b == 0x00:
        print(f'  [NUL at 0x{i:x}]', end='')
        i += 1
    elif 0x20 <= b < 0x7f:
        print(chr(b), end='')
        i += 1
    else:
        # Binary data - show as hex until next printable run
        hex_run = []
        while i < 0x600 and not (0x20 <= raw[i] < 0x7f or raw[i] == 0x0a):
            hex_run.append(f'{raw[i]:02x}')
            i += 1
        if hex_run:
            print(f'  <{" ".join(hex_run[:16])}{"..." if len(hex_run)>16 else ""}>', end='')

print()
print()

# Find all NUL-terminated strings in the header
print('=== NULL-TERMINATED STRINGS in first 0x600 bytes ===')
start = 0
strings = []
for i in range(0x600):
    if raw[i] == 0:
        if i - start >= 4:
            s = raw[start:i]
            try:
                decoded = s.decode('utf-8')
                if any(c.isalpha() for c in decoded):
                    strings.append((start, decoded))
            except:
                pass
        start = i + 1
for off, s in strings:
    print(f'  0x{off:04x}: {repr(s)}')

# Check if there's a structured table after the header
# Look for repeating patterns
print()
print('=== Scanning for node magic / LOVE tag ===')
# Header says "nodes are LOVE-tagged"
love_tag = b'LOVE'
for i in range(size - 4):
    if raw[i:i+4] == love_tag:
        print(f'  LOVE tag at 0x{i:x}')
        # Print surrounding context
        ctx_start = max(0, i-16)
        ctx = raw[ctx_start:i+64]
        for j in range(0, len(ctx), 16):
            chunk = ctx[j:j+16]
            hex_s = ' '.join(f'{b:02x}' for b in chunk)
            asc_s = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in chunk)
            print(f'    0x{ctx_start+j:06x}: {hex_s:<48}  {asc_s}')
        print()

print()
print('=== Look for "DEAD" tag (dead/freed nodes?) ===')
dead_tag = b'DEAD'
dead_count = 0
for i in range(size - 4):
    if raw[i:i+4] == dead_tag:
        dead_count += 1
        if dead_count <= 5:
            print(f'  DEAD tag at 0x{i:x}: {raw[i:i+32].hex()}')
print(f'Total DEAD tags: {dead_count}')

# Look for the node list head explicitly
# The HEARTLIST VA = 0x555555458000
# What if nodes are stored in the file at fixed offsets?
# The file is 109424 bytes. Maybe it's organized as pages.
# 109424 / 4096 = 26.7 pages of 4096 bytes
# Or 109424 / 0x1000 = 26 full pages + partial

print()
print('=== Check for section markers / magic numbers ===')
magic_patterns = [
    (b'\xde\xad\xbe\xef', 'DEADBEEF'),
    (b'\xca\xfe\xba\xbe', 'CAFEBABE'),
    (b'\xfe\xed\xfa\xce', 'FEEDFACE'),
    (b'NODE', 'NODE'),
    (b'HEAP', 'HEAP'),
    (b'LIST', 'LIST'),
    (b'HEAD', 'HEAD'),
    (b'NEXT', 'NEXT'),
    (b'heartd', 'heartd'),
    (b'FEEL', 'FEEL'),
    (b'NOTE', 'NOTE'),
    (b'CONF', 'CONF'),
]
for pattern, name in magic_patterns:
    idx = 0
    count = 0
    while True:
        idx = raw.find(pattern, idx)
        if idx == -1:
            break
        count += 1
        if count <= 3:
            print(f'  {name} at 0x{idx:x}: {raw[idx:idx+24].hex()}')
        idx += 1
    if count > 0:
        print(f'  Total {name}: {count}')
