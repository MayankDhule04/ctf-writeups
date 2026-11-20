#!/usr/bin/env python3
"""Walk the actual linked list chains in the full heart dump"""
import struct

with open('heart_full.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000

def va_to_off(va):
    return va - image_base if va else None

def read_u64(off):
    if off is not None and 0 <= off <= size - 8:
        return struct.unpack_from('<Q', raw, off)[0]
    return None

def read_u32(off):
    if off is not None and 0 <= off <= size - 4:
        return struct.unpack_from('<I', raw, off)[0]
    return None

# Scan ALL LOVE/DEAD nodes
print('=== All LOVE/DEAD nodes ===')
nodes = []
for off in range(0, size - 64, 8):
    tag4 = raw[off:off+4]
    if tag4 in (b'LOVE', b'DEAD'):
        tag = tag4.decode()
        flags_seq = read_u64(off + 8)
        next_va = read_u64(off + 16)
        key = read_u32(off + 24)
        extra = read_u32(off + 28)
        masked_data = read_u64(off + 32) if off + 40 <= size else None
        
        next_off = va_to_off(next_va) if next_va else None
        next_in_file = (next_off is not None and 0 <= next_off < size)
        
        nodes.append({
            'off': off,
            'va': image_base + off,
            'tag': tag,
            'flags_seq': flags_seq,
            'next_va': next_va,
            'next_off': next_off,
            'key': key,
            'extra': extra,
            'masked_data': masked_data,
        })
        
        # XOR key with data to get character
        if key is not None and masked_data is not None:
            # Try various interpretations
            char_candidate = masked_data ^ key
            char_byte = char_candidate & 0xFF
            if 0x20 <= char_byte < 0x7f:
                char = chr(char_byte)
            else:
                char = '?'
            
            # Alt: just XOR the 4-byte key with first 4 bytes of data
            data4 = read_u32(off + 32)
            char2_val = (data4 ^ key) & 0xFF if data4 is not None else 0
            char2 = chr(char2_val) if 0x20 <= char2_val < 0x7f else '?'
            
            noff_str = f'0x{next_off:x}' if next_off is not None else 'None'
            print(f'  0x{off:06x} {tag} seq={flags_seq:016x} next->{noff_str} key=0x{key:08x} data=0x{masked_data:016x} char={char} char2={char2}')

print(f'\nTotal LOVE nodes: {sum(1 for n in nodes if n["tag"]=="LOVE")}')
print(f'Total DEAD nodes: {sum(1 for n in nodes if n["tag"]=="DEAD")}')

# Build a map
node_by_off = {n['off']: n for n in nodes}
node_by_va  = {n['va']: n for n in nodes}

print()
print('=== Walking chains from each LOVE node ===')
visited_global = set()

all_chains = []
for n in nodes:
    if n['tag'] != 'LOVE' or n['off'] in visited_global:
        continue
    
    chain = []
    curr_off = n['off']
    visited = set()
    
    while curr_off is not None and curr_off in node_by_off and curr_off not in visited:
        node = node_by_off[curr_off]
        visited.add(curr_off)
        
        # Get character from this node
        key = node['key']
        data4 = read_u32(curr_off + 32)
        if key is not None and data4 is not None:
            char_val = (data4 ^ key) & 0xFF
            char = chr(char_val) if 0x20 <= char_val < 0x7f else f'[{char_val:02x}]'
        else:
            char = '?'
        
        chain.append((curr_off, node['tag'], char))
        
        # Follow next pointer (skip DEAD nodes or include them?)
        next_off = node['next_off']
        if next_off is None or next_off not in node_by_off:
            break
        curr_off = next_off
    
    if len(chain) >= 2:
        all_chains.append(chain)
        visited_global.update(off for off, _, _ in chain)
        text = ''.join(c for _, _, c in chain)
        print(f'  Chain from 0x{chain[0][0]:x} len={len(chain)}: {text}')

print()
print('=== Now checking: what if we skip DEAD nodes? ===')
for n in nodes:
    if n['tag'] != 'LOVE':
        continue
    
    # Walk only through LOVE nodes
    chain = []
    curr_off = n['off']
    visited = set()
    
    while curr_off is not None and curr_off not in visited:
        if curr_off not in node_by_off:
            break
        node = node_by_off[curr_off]
        if node['tag'] == 'DEAD':
            # Skip dead nodes - follow their pointer but don't include data
            next_off = node['next_off']
            curr_off = next_off
            continue
        
        visited.add(curr_off)
        
        key = node['key']
        data4 = read_u32(curr_off + 32)
        if key is not None and data4 is not None:
            char_val = (data4 ^ key) & 0xFF
            char = chr(char_val) if 0x20 <= char_val < 0x7f else f'[{char_val:02x}]'
        else:
            char = '?'
        
        chain.append((curr_off, char))
        
        next_off = node['next_off']
        if next_off is None:
            break
        curr_off = next_off
    
    if len(chain) >= 3:
        text = ''.join(c for _, c in chain)
        if any(c.isalpha() for c in text):
            print(f'  Chain from 0x{chain[0][0]:x} len={len(chain)}: {text}')

print()
print('=== Try different offsets within node for the character ===')
# Maybe the masked char is at a different offset
for char_offset_in_node in [24, 28, 32, 33, 36, 40, 44, 48]:
    results = []
    for n in nodes:
        if n['tag'] != 'LOVE':
            continue
        key = n['key']
        if key is None:
            continue
        char_raw = raw[n['off'] + char_offset_in_node] if n['off'] + char_offset_in_node < size else 0
        c = char_raw ^ (key & 0xFF)
        if 0x20 <= c < 0x7f:
            results.append(chr(c))
        else:
            results.append('.')
    
    text = ''.join(results)
    if 'CHAKRA' in text or text.count('.') < len(text) // 2:
        print(f'  char at +{char_offset_in_node}: {text[:60]}')
