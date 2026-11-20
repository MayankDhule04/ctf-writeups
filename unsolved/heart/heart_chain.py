#!/usr/bin/env python3
"""
The real approach: find pointer chains in the masked heap.

If each node has structure:
  struct Node {
    uint64_t next_ptr;   // VA of next node, XOR'd with node_key
    uint64_t node_key;   // the per-node XOR key
    uint8_t  masked_char; // flag char XOR'd with (node_key & 0xFF) perhaps
    uint8_t  pad[7];
  };

Then: real_next = next_ptr XOR node_key
And: real_char = masked_char XOR (node_key & 0xFF) or similar

Also: if "LOVE-tagged", maybe bits 0-3 of the tag word are 'LOVE' after XOR.

Let me try: node at offset O has:
  raw[O:O+8] = next_ptr XOR key  (masked next)
  raw[O+8:O+16] = key             (stored plaintext? or also masked?)
  raw[O+16] = char XOR key_byte   (masked char)

If key is stored plaintext, I can find nodes where key = raw[O+8:O+16] makes
real_next = raw[O:O+8] XOR key a valid VA, AND real_next points to another such node.

Let's try this!
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000

# Try NODE_SIZE = 24: [8 masked_next][8 key][1 char][7 pad]
# Try NODE_SIZE = 32: [8 masked_next][8 key][1 char][15 pad]
# Try NODE_SIZE = 16: [8 masked_next][8 key_and_char]

def try_node_structure(node_size, next_off, key_off, char_off):
    """
    Try to find linked list chains with given node layout.
    - next_off: offset within node of masked next pointer
    - key_off: offset within node of XOR key (plaintext stored)
    - char_off: offset within node of masked character
    """
    VA_LO = image_base
    VA_HI = image_base + size
    
    # Build a map of offset -> (next_va, key, char) for all potential nodes
    nodes = {}
    for off in range(0, size - node_size, 8):  # 8-byte aligned
        masked_next = struct.unpack_from('<Q', raw, off + next_off)[0]
        key = struct.unpack_from('<Q', raw, off + key_off)[0]
        
        # Unmask the next pointer
        real_next = masked_next ^ key
        
        if real_next == 0:  # null = end of list
            c = raw[off + char_off] ^ (key & 0xFF)
            if 0x20 <= c < 0x7f:
                nodes[off] = (0, key, chr(c))
        elif VA_LO <= real_next < VA_HI:
            next_file_off = real_next - VA_LO
            if next_file_off % 8 == 0:  # aligned
                c = raw[off + char_off] ^ (key & 0xFF)
                if 0x20 <= c < 0x7f:
                    nodes[off] = (next_file_off, key, chr(c))
    
    if not nodes:
        return []
    
    # Try to walk chains starting from each node
    chains = []
    node_set = set(nodes.keys())
    visited_global = set()
    
    for start_off in node_set:
        if start_off in visited_global:
            continue
        
        # Walk the chain
        chain = []
        curr = start_off
        visited = set()
        
        while curr in nodes and curr not in visited:
            visited.add(curr)
            next_off_val, key, ch = nodes[curr]
            chain.append((curr, ch))
            if next_off_val == 0:
                break
            curr = next_off_val
        
        if len(chain) >= 7:  # minimum: "CHAKRA{"
            flag_str = ''.join(c for _, c in chain)
            if 'CHAKRA' in flag_str or flag_str.startswith('C'):
                chains.append(chain)
                visited_global.update(visited)
    
    return chains

# Try various node structures
configs = [
    (16, 0, 8, 0),   # [masked_next:8][key:8], char uses low byte of next?
    (24, 0, 8, 16),  # [masked_next:8][key:8][char:1][pad:7]
    (24, 8, 0, 16),  # [key:8][masked_next:8][char:1][pad:7]
    (32, 0, 8, 16),  # [masked_next:8][key:8][char:1][pad:15]
    (32, 0, 8, 24),  # [masked_next:8][key:8][pad:8][char:1][pad:7]
    (48, 0, 8, 16),
    (64, 0, 8, 16),
    (64, 0, 8, 32),
    # key might be 4 bytes
]

print('Testing node configurations...')
for node_size, next_field, key_field, char_field in configs:
    chains = try_node_structure(node_size, next_field, key_field, char_field)
    if chains:
        print(f'\nFOUND chains! node_size={node_size} next@{next_field} key@{key_field} char@{char_field}')
        for chain in chains[:3]:
            flag = ''.join(c for _, c in chain)
            print(f'  len={len(chain)}: {flag[:80]}')

print()
print('=== Alternative: key might be the node address itself ===')
# char XOR (va & 0xFF) or char XOR (va >> 12 & 0xFF) etc.
# Let's try: char XOR ((image_base + offset) >> 8 & 0xFF)
# At offset 0x8000: key = (0x555555408000 >> 8) & 0xFF = 0x80
# raw[0x8000] = 0x73 ('s' in CHAKRA{s...)
# Hmm, but CHAKRA is NOT XOR'd: 0x43 != 0x73 XOR 0x80 = 0xF3. 
# So that decoy IS plaintext (key = 0 for those nodes).

# Try: the nodes are not sequential. Let me look for a different structure entirely.
# Maybe the "next" pointer IS stored in plaintext, but other data is masked.

print('Scanning for raw plaintext VA pointers as next pointers...')
VA_LO = image_base
VA_HI = image_base + size

# Find all locations where a 64-bit value is a valid VA
all_va_locations = []
for off in range(0x200, size - 8, 8):
    val = struct.unpack_from('<Q', raw, off)[0]
    if VA_LO <= val < VA_HI:
        all_va_locations.append((off, val))

print(f'Found {len(all_va_locations)} raw VA values')

# Build graph: where does each VA-containing location point?
# and can we find chains?
va_map = {off: (val - VA_LO) for off, val in all_va_locations}

# Find chains of length >= 5
print('Looking for chains in raw VA references...')
for start_off, target_off in list(va_map.items())[:]:
    # Try to walk: each node at aligned boundary, first 8 bytes = next ptr
    chain = [start_off]
    curr = target_off
    visited = {start_off}
    while curr in va_map and curr not in visited:
        visited.add(curr)
        chain.append(curr)
        curr = va_map[curr]
        if len(chain) > 100:
            break
    
    if len(chain) >= 5:
        print(f'  Chain of {len(chain)} from 0x{start_off:x}: {[hex(x) for x in chain[:10]]}')
