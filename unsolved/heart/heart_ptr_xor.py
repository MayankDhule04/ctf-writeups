#!/usr/bin/env python3
"""
New hypothesis based on "linked by pointers":

The node structure might be:
  struct Node {
    uintptr_t next;     // plaintext next pointer (VA)  
    uint8_t   data;     // char XOR'd with (this_node_va & 0xFF)
    // more padding
  };

But we showed there are NO raw VA values in the file.

Alternative: maybe the XOR key for the pointer IS the pointer's value, 
creating a self-referential encryption. Like:
  stored = real_ptr XOR key
  key = stored XOR some_constant

Or: the next pointer is stored as: next_ptr XOR current_ptr
(relative encoding)

Or: all pointers XOR'd with a single global key.

Let me try: find a single 64-bit constant K such that applying K XOR to 
8-byte aligned values in the file produces valid heap VAs.
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000
VA_LO = image_base
VA_HI = image_base + size

# Approach: brute force all possible 8-byte XOR keys that are themselves
# heap addresses (since the key might be another VA or a simple value)
# 
# For each 8-byte aligned position in the file, 
# count how many other positions XOR'd with the value at that position
# give valid VAs. If many -> that might be the global XOR key.

print('=== Finding potential global XOR key ===')
print('(Testing first 8-byte value at each position as a potential key)')

best_key = None
best_count = 0
best_candidates = []

# Sample positions to test as keys (every 256 bytes)
for key_off in range(0x200, min(0x2000, size - 8), 256):
    key = struct.unpack_from('<Q', raw, key_off)[0]
    if key == 0:
        continue
    
    # Count how many aligned values in file, XOR'd with key, give valid VAs
    count = 0
    va_targets = []
    for off in range(0x200, size - 8, 8):
        val = struct.unpack_from('<Q', raw, off)[0]
        unmasked = val ^ key
        if VA_LO <= unmasked < VA_HI:
            count += 1
            va_targets.append((off, unmasked))
    
    if count > best_count:
        best_count = count
        best_key = key
        best_candidates = va_targets[:20]

print(f'Best key: 0x{best_key:016x} at some offset, produces {best_count} valid VAs')
if best_candidates:
    print('Sample VA targets:')
    for off, va in best_candidates[:10]:
        target_off = va - VA_LO
        ttext = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[target_off:target_off+8])
        print(f'  file[0x{off:x}] XOR key -> VA 0x{va:x} (file off 0x{target_off:x}) [{ttext}]')

print()
print('=== Alternative: Look at the problem as a C program ===')
# The challenge title is "Love Core Memory" and the binary is called "heartd"
# It's a daemon that crashed with SIGSEGV while CONFESSING.
# The linked list contains "notes" (words/chars) that form a confession.
#
# Standard CTF linked list format:
# struct node_t {
#     struct node_t *next;  // 8 bytes
#     uint64_t key;         // 8 bytes  
#     char payload[];       // variable
# };
#
# The LOVE tag is probably part of the node:
# struct node_t {
#     uint32_t tag;         // 'LOVE' = 0x4C4F5645
#     uint32_t seq;         // sequence number
#     struct node_t *next;  // 8 bytes, XOR'd with key
#     uint64_t key;         // 8 bytes, the XOR mask
#     char payload[8];      // 8 bytes, XOR'd with key
#     // total: 32 bytes
# };
#
# If we XOR the first 4 bytes of each 32-byte block with the value that gives 'LOVE':
# raw[off:off+4] XOR key4 = b'LOVE'
# key4 = raw[off:off+4] XOR b'LOVE'

NODE_SIZE = 32
LOVE = struct.unpack('<I', b'LOVE')[0]

print(f'Testing {NODE_SIZE}-byte nodes where tag XOR key = "LOVE"...')
love_nodes = []
for off in range(0, size - NODE_SIZE, NODE_SIZE):
    tag_val = struct.unpack_from('<I', raw, off)[0]
    key4 = tag_val ^ LOVE
    # The rest of the node is XOR'd with this key (repeated or extended)
    # Try: key = key4 repeated as 8 bytes: key64 = key4 | (key4 << 32)
    key64 = key4 | (key4 << 32)
    
    # Unmask next pointer
    masked_next = struct.unpack_from('<Q', raw, off + 8)[0]
    real_next = masked_next ^ key64
    
    # Unmask payload
    payload = bytes(raw[off + 24 + i] ^ ((key4 >> (8*(i%4))) & 0xFF) for i in range(8))
    text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in payload)
    
    if VA_LO <= real_next < VA_HI or real_next == 0:
        love_nodes.append((off, key4, real_next, text))

print(f'Found {len(love_nodes)} potential LOVE-tagged nodes')
for off, key4, next_va, text in love_nodes[:20]:
    next_off = next_va - VA_LO if next_va else 0
    print(f'  off=0x{off:06x} key=0x{key4:08x} next=0x{next_va:x} (off=0x{next_off:x}) payload=[{text}]')

# Walk chains
if love_nodes:
    node_map = {off: (key4, next_va, text) for off, key4, next_va, text in love_nodes}
    va_to_off = {(off + VA_LO): off for off in node_map}
    
    print()
    print('Walking chains...')
    for start_off in node_map:
        chain = []
        curr_off = start_off
        visited = set()
        while curr_off in node_map and curr_off not in visited:
            visited.add(curr_off)
            key4, next_va, text = node_map[curr_off]
            chain.append(text)
            if next_va == 0:
                break
            next_off = next_va - VA_LO
            curr_off = next_off
        
        if len(chain) >= 5:
            result = ''.join(chain)
            if any(c.isalpha() for c in result):
                print(f'  start=0x{start_off:x} len={len(chain)}: {result[:60]}')
