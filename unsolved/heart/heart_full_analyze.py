#!/usr/bin/env python3
"""Analyze the full 1.5MB heart dump"""
import struct

with open('heart_full.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000
print(f'Full dump size: {size} bytes = 0x{size:x}')

# Find all CHAKRA strings
print('\n=== All plaintext CHAKRA strings ===')
idx = 0
while True:
    idx = raw.find(b'CHAKRA', idx)
    if idx == -1:
        break
    end = raw.find(b'}', idx)
    if end != -1 and end - idx < 100:
        print(f'  0x{idx:x}: {raw[idx:end+1].decode(errors="replace")}')
    idx += 1

# Check around the new CHAKRA at 0x150000
print('\n=== Region around 0x150000 ===')
for off in range(0x14FF00, 0x150200, 8):
    val = struct.unpack_from('<Q', raw, off)[0] if off + 8 <= size else 0
    text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
    note = ' <-- THIRD CHAKRA' if off == 0x150000 else ''
    print(f'  0x{off:06x}: {val:016x}  {text}{note}')

# Look for VA pointers in the full dump
print('\n=== VA-like 64-bit values in full dump ===')
VA_LO = image_base
VA_HI = image_base + size
va_refs = []
for off in range(0, size - 8, 8):
    val = struct.unpack_from('<Q', raw, off)[0]
    if VA_LO <= val < VA_HI:
        va_refs.append((off, val))

print(f'Total VA values: {len(va_refs)}')
for off, val in va_refs[:20]:
    target_off = val - VA_LO
    ttext = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[target_off:target_off+8])
    print(f'  0x{off:x}: VA=0x{val:x} -> off=0x{target_off:x} [{ttext}]')

# Look for node chains with VA pointers
if va_refs:
    print('\nBuilding pointer graph...')
    ptr_map = {}
    for off, val in va_refs:
        target = val - VA_LO
        ptr_map[off] = target
    
    # Find chains
    for start in list(ptr_map.keys())[:]:
        chain_offs = [start]
        curr = ptr_map.get(start)
        visited = {start}
        while curr is not None and curr not in visited and curr in ptr_map:
            visited.add(curr)
            chain_offs.append(curr)
            curr = ptr_map.get(curr)
        
        if len(chain_offs) >= 5:
            # Extract possible characters from each node
            chars = []
            for node_off in chain_offs:
                # Try char at various positions within the node
                for char_pos in [8, 16, 24]:
                    if node_off + char_pos < size:
                        c = raw[node_off + char_pos]
                        if 0x20 <= c < 0x7f:
                            chars.append(chr(c))
                            break
            print(f'  Chain from 0x{start:x}, len={len(chain_offs)}: {" ".join(chars[:20])}')

# Now try XOR approach with full dump
print('\n=== Searching for XOR-masked CHAKRA{ in full dump ===')
# Since third CHAKRA is plaintext too, maybe there's a 4th that IS the flag
# Try single-byte XOR keys on each 8-byte block and see if any form CHAKRA{
for key in range(1, 256):
    for off in range(0x200, size - 50, 8):
        if raw[off] ^ key == ord('C') and raw[off+1] ^ key == ord('H'):
            candidate = bytes(b ^ key for b in raw[off:off+7])
            if candidate == b'CHAKRA{':
                end = off + 7
                flag = 'CHAKRA{'
                for i in range(7, 80):
                    if off + i >= size:
                        break
                    c = raw[off+i] ^ key
                    if chr(c) == '}':
                        flag += '}'
                        break
                    if 0x20 <= c < 0x7f:
                        flag += chr(c)
                    else:
                        break
                if '}' in flag and len(flag) > 10:
                    print(f'  key=0x{key:02x} off=0x{off:x}: {flag}')

# Also try with the node-based scheme where we look for sequential nodes
# containing one XOR'd char each, the key being the last byte of the node's VA
print('\n=== One-char-per-node with key = (VA & 0xFF) ===')
# VA = image_base + file_offset
# key = VA & 0xFF = (image_base + offset) & 0xFF = offset & 0xFF (since base ends in 0x000000)
# So key[i] = (i % 256)
# decrypted[i] = raw[i] ^ (i & 0xFF)
decrypted = bytearray(size)
for i in range(size):
    decrypted[i] = raw[i] ^ (i & 0xFF)

idx = 0
while True:
    idx = bytes(decrypted).find(b'CHAKRA{', idx)
    if idx == -1:
        break
    end_idx = bytes(decrypted).find(b'}', idx)
    if end_idx != -1 and end_idx - idx < 80:
        print(f'  0x{idx:x}: {decrypted[idx:end_idx+1].decode(errors="replace")}')
    idx += 1
