#!/usr/bin/env python3
"""
Full decode of the heart dump.
Node structure discovered:
  +0:  uint32_t tag     (LOVE=0x45564f4c or DEAD=0x44414544)
  +4:  uint32_t pad0
  +8:  uint32_t flags   (0xe or 0x10 etc.)
  +12: uint32_t seq_num (sequence index)
  +16: uint64_t next    (VA of next node)
  +24: uint32_t key     (XOR key)
  +28: uint32_t pad1
  +32: uint64_t data    (some field, with char at +32 XOR key = char sometimes)
  +40: potentially more data

Sequence numbers in LOVE nodes: 0,1,2,3,4,5,...,0x29,0x2a,0x2b,0x1b,0x1c,0x25,0x28
That means there are nodes with seq 0..0x2b = 0..43, suggesting ~44 character flag.

Let's collect ALL nodes, sort by sequence number, and decode.
"""
import struct

with open('heart_full.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000

def va_to_off(va):
    return va - image_base

def read_u32(off):
    if 0 <= off <= size - 4:
        return struct.unpack_from('<I', raw, off)[0]
    return None

def read_u64(off):
    if 0 <= off <= size - 8:
        return struct.unpack_from('<Q', raw, off)[0]
    return None

# Collect ALL nodes
nodes = []
for off in range(0, size - 64, 8):
    tag4 = raw[off:off+4]
    if tag4 not in (b'LOVE', b'DEAD'):
        continue
    
    tag = tag4.decode()
    pad0 = read_u32(off + 4)
    if pad0 != 0:  # validate: padding should be 0
        continue
    
    flags = read_u32(off + 8)
    seq = read_u32(off + 12)
    next_va = read_u64(off + 16)
    key = read_u32(off + 24)
    
    next_off = va_to_off(next_va) if next_va and next_va != 0 else None
    
    nodes.append({
        'off': off,
        'va': image_base + off,
        'tag': tag,
        'flags': flags,
        'seq': seq,
        'next_va': next_va,
        'next_off': next_off,
        'key': key,
    })

print(f'Total nodes found: {len(nodes)}')
print(f'  LOVE: {sum(1 for n in nodes if n["tag"]=="LOVE")}')
print(f'  DEAD: {sum(1 for n in nodes if n["tag"]=="DEAD")}')
print()

# Print all nodes sorted by seq
print('=== All nodes (sorted by seq) ===')
love_nodes = sorted([n for n in nodes if n['tag']=='LOVE'], key=lambda n: n['seq'])
dead_nodes = [n for n in nodes if n['tag']=='DEAD']

for n in love_nodes:
    # Try multiple char offset candidates
    chars = []
    for char_off in [32, 33, 36, 40, 41, 44]:
        if n['off'] + char_off < size:
            raw_byte = raw[n['off'] + char_off]
            c = raw_byte ^ (n['key'] & 0xFF)
            chars.append(f'+{char_off}:{chr(c) if 0x20<=c<0x7f else f"[{c:02x}]"}')
    
    # Also try XOR with full 4-byte key (repeat key bytes)
    for data_off in [32, 36, 40]:
        if n['off'] + data_off + 4 <= size:
            data4 = read_u32(n['off'] + data_off)
            c = (data4 ^ n['key']) & 0xFF
            chars.append(f'xor4+{data_off}:{chr(c) if 0x20<=c<0x7f else f"[{c:02x}]"}')
    
    print(f'  seq={n["seq"]:3d} off=0x{n["off"]:06x} key=0x{n["key"]:08x} | {" | ".join(chars)}')

print()
print('=== Trying to build flag string ===')
# Sort love nodes by sequence number and extract chars
# Need to figure out correct char extraction

# From previous output, at +32 with key & 0xFF:
# seq=4 -> char='L' (0x4c). key=0x6472e068, key&0xFF=0x68. data[32]=? 
# 0x4c ^ 0x68 = 0x24. Let's verify:

n4 = next((n for n in love_nodes if n['seq'] == 4), None)
if n4:
    off = n4['off']
    key = n4['key']
    raw_at_32 = raw[off + 32]
    raw_at_36 = raw[off + 36]
    print(f'seq=4: key=0x{key:08x}, raw[+32]=0x{raw_at_32:02x}, raw[+36]=0x{raw_at_36:02x}')
    print(f'  +32 XOR key&0xFF = 0x{raw_at_32 ^ (key&0xFF):02x} = {chr(raw_at_32 ^ (key&0xFF)) if 0x20<=raw_at_32^(key&0xFF)<0x7f else "?"}')
    print(f'  Expecting "L" (0x4c)')
    # If raw_at_32 ^ (key&0xFF) != 0x4c:
    # Then the XOR scheme is different. Let's check all 4 key bytes
    for shift in [0, 8, 16, 24]:
        kb = (key >> shift) & 0xFF
        c = raw_at_32 ^ kb
        print(f'  +32 XOR key[{shift//8}]=0x{kb:02x} = 0x{c:02x} = {chr(c) if 0x20<=c<0x7f else "?"}')

# Collect chars using multiple methods
print()
print('=== Flag extraction attempt ===')
flag_chars = {}  # seq -> char

for n in love_nodes:
    off = n['off']
    key = n['key']
    seq = n['seq']
    
    # Method 1: byte at +32 XOR (key & 0xFF)
    c1 = raw[off+32] ^ (key & 0xFF) if off+32 < size else 0
    # Method 2: byte at +32 XOR ((key>>8) & 0xFF)
    c2 = raw[off+32] ^ ((key>>8) & 0xFF) if off+32 < size else 0
    # Method 3: byte at +36 XOR (key & 0xFF)
    c3 = raw[off+36] ^ (key & 0xFF) if off+36 < size else 0
    # Method 4: u32 at +32 XOR key, take low byte
    d32 = read_u32(off+32)
    c4 = ((d32 ^ key) & 0xFF) if d32 else 0
    # Method 5: u32 at +36 XOR key
    d36 = read_u32(off+36)
    c5 = ((d36 ^ key) & 0xFF) if d36 else 0
    
    print(f'  seq={seq:3d} m1={chr(c1) if 0x20<=c1<0x7f else "?"} '
          f'm2={chr(c2) if 0x20<=c2<0x7f else "?"} '
          f'm3={chr(c3) if 0x20<=c3<0x7f else "?"} '
          f'm4={chr(c4) if 0x20<=c4<0x7f else "?"} '
          f'm5={chr(c5) if 0x20<=c5<0x7f else "?"}')

# Now check the XOR of all 4 bytes:
print()
print('=== Checking all 4 key bytes against data at +32 ===')
for n in love_nodes[:5]:
    off = n['off']
    key = n['key']
    print(f'  seq={n["seq"]} key=0x{key:08x}:')
    for data_pos in range(32, 64, 1):
        if off + data_pos >= size:
            break
        b = raw[off + data_pos]
        for shift in range(0, 32, 8):
            kb = (key >> shift) & 0xFF
            c = b ^ kb
            if 0x20 <= c < 0x7f:
                print(f'    data[+{data_pos}]=0x{b:02x} XOR key[{shift//8}]=0x{kb:02x} = {chr(c)}')
