#!/usr/bin/env python3
"""
The challenge says: "walk what remains of its heart"
"each masked so a casual glance sees nothing, linked by pointers"

Key: the nodes ARE linked by pointers. We need to follow the chain.
The pointers are in the file somewhere. They're masked (XOR'd).

Let me think about this differently:
- We have two PLAINTEXT chakra nodes at offsets 0x8000 and 0x9800
- "nodes are LOVE-tagged" - maybe LOVE = 0x4C4F5645 is the tag/magic
- These plaintext nodes are DECOYS ("the freed ones lie")

The REAL nodes are XOR'd. We need to find them by:
1. Finding what a node looks like (size, layout)
2. Finding a chain of pointers

Looking at the two decoy nodes:
- Decoy 1 at file 0x8000: contains "CHAKRA{str1ngs_w0nt_s4v3_y0u}"
- Decoy 2 at file 0x9800: contains "CHAKRA{th3_r34l_0n3_1s_x0r3d_p3r_n0d3}"

Let's figure out node size. After the CHAKRA text there's binary data.
Let me look at both decoy regions carefully and try to find the next pointer.

If a node is:
struct note {
    uint64_t  next;      // masked pointer to next node  
    uint32_t  key;       // XOR key for the data byte
    uint8_t   tag[4];    // "LOVE" or "DEAD"
    char      data[...]; // the masked character(s)
};

Or maybe:
struct note {
    uint32_t  tag;       // "LOVE" or "DEAD"  
    uint8_t   key;       // single byte XOR key
    uint8_t   data;      // single masked char
    uint16_t  pad;
    uint64_t  next;      // next ptr (also masked?)
};

The decoy at 0x8000 has "CHAKRA{str1ngs_w0nt_s4v3_y0u}" = 30 bytes.
If the node stores the WHOLE fake flag as a string, then node_data_size = 30+ bytes.
But the real chain has one char per node ("each masked").

So the DECOY nodes store a full fake string.
The REAL nodes store ONE character each, XOR'd with a per-node key.

For real nodes of size N bytes each:
- Contains one masked char
- Contains a next pointer
- The key might be the node's own VA

Let's try to find a valid pointer structure in the file.
Approach: scan ALL 8-byte aligned positions for values that look like valid heap VAs.

The heap for a typical Linux process with image_base=0x555555400000:
- Heap starts at around 0x555555600000 (after BSS)
- Or might be at 0x555555458000+ (as HEARTLIST suggests)

Wait - HEARTLIST = 0x555555458000 is where the HEAD POINTER IS STORED.
The HEAD POINTER VALUE points to the FIRST NODE.

Since HEARTLIST is at file_off = 0x58000 (with original base), which is beyond file,
there's a problem. But what if I have the base wrong?

Let me try: what if the dump is NOT based on image_base, but on HEARTLIST?
i.e., the file starts at VA 0x555555458000?
Then file[0] corresponds to VA 0x555555458000.

The header ("=== heartd core dump ===") would be at VA 0x555555458000.
CHAKRA decoy at file offset 0x8000 = VA 0x555555460000.

Let's check if any 8-byte values at file[0:8] XOR'd appropriately give a heap VA.
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)

# Approach: Treat file as starting at various possible base addresses
# and look for self-consistent pointer chains

def try_base(base_va, label=""):
    """Try to walk a linked list assuming file starts at base_va"""
    VA_LO = base_va
    VA_HI = base_va + size
    
    def va_to_off(va):
        return va - base_va
    
    def read_u64(off):
        if 0 <= off <= size - 8:
            return struct.unpack_from('<Q', raw, off)[0]
        return None
    
    # Find all 8-byte values that are valid VAs (unmasked)
    raw_vas = []
    for off in range(0, size - 8, 8):
        val = read_u64(off)
        if val is not None and VA_LO <= val < VA_HI:
            raw_vas.append((off, val))
    
    if raw_vas:
        print(f'Base 0x{base_va:x} ({label}): {len(raw_vas)} raw VA values')
        for off, val in raw_vas[:5]:
            text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
            print(f'  0x{off:x}: 0x{val:x} [{text}]')
    
    # Try XOR-masked VAs: raw[off] ^ mask = VA, where mask is the stored value before
    # or at some known location
    # This is complex, let's focus on raw VAs first
    return raw_vas

# Test multiple possible bases
for base in [
    0x555555400000,  # original (heap range 0-109k)
    0x555555440000,  # alternative  
    0x555555450000,  # so CHAKRA1 at 0x8000 = VA 0x555555458000
    0x555555458000,  # file starts at HEARTLIST
    0x555555460000,
]:
    try_base(base, f'file_off_0x{base - 0x555555400000:x}')

print()
print('=== Looking at the actual structure more carefully ===')
# The HEARTLIST var is at VA 0x555555458000.
# With original base (0x555555400000), this would be at file offset 0x58000 = 360448.
# But file is only 109424 = 0x1AB70 bytes.
# 
# HOWEVER: what if the file doesn't represent a contiguous memory region?
# What if it's the heap ALLOCATOR output, which has internal structure?
#
# malloc heap layout:
# [prev_size][size|flags][user_data...]
# Or glibc malloc chunks:
# chunk: [prev_size:8][size:8][fd:8][bk:8][user_data...]
# 
# Let's look at the file as a heap with malloc chunks
# and find chunks that contain LOVE-tagged data

print('Scanning for potential malloc chunks (size field pattern):')
MMAP_THRESH = 0x20000  # typical mmap threshold
chunk_count = 0
off = 0x200  # skip header

while off < size - 16:
    # glibc malloc chunk: [prev_size][size_with_flags][data...]
    prev_size = struct.unpack_from('<Q', raw, off)[0]
    size_field = struct.unpack_from('<Q', raw, off + 8)[0]
    
    # Extract actual size (mask off the flag bits: P=prev_inuse, M=mmap, A=arena)
    chunk_size = size_field & ~0x7
    
    if 0x10 <= chunk_size <= 0x1000 and (size_field & 1):  # reasonable size, prev_inuse set
        # This looks like an allocated chunk
        data_off = off + 16  # after header
        data = raw[data_off:data_off+min(chunk_size-16, 64)]
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in data[:16])
        chunk_count += 1
        if chunk_count <= 10 or b'LOVE' in data or b'CHAKRA' in data:
            print(f'  off=0x{off:x} prev_size=0x{prev_size:x} chunk_size=0x{chunk_size:x}: [{text}]')
        off += chunk_size
    else:
        off += 8  # step through

print(f'Total possible chunks: {chunk_count}')

print()
print('=== Nuclear option: try every possible node alignment and XOR key ===')
# The real flag has format CHAKRA{...}
# Try: for each offset in file, assume it's a node with single byte,
# XOR'd with some small key (0-255), check if result is printable
# Then look for sequences that spell CHAKRA{...}

# For each byte position, what keys make it a valid flag character?
valid_flag_chars = set('CHAKRchakr{}0123456789_abcdefghijklmnopqrstuvwxyz!@#$%^&*()')

flag_byte_candidates = {}  # off -> list of (key, char)
for off in range(0x200, size):
    for key in range(256):
        c = raw[off] ^ key
        if chr(c) in valid_flag_chars:
            if off not in flag_byte_candidates:
                flag_byte_candidates[off] = []
            flag_byte_candidates[off].append((key, chr(c)))

# Look for "CHAKRA{" starting at various offsets
# We need 7 consecutive offsets where applying keys gives C,H,A,K,R,A,{
# and the keys follow some pattern (same key, sequential addresses, etc.)
print(f'Total offsets with valid flag char candidates: {len(flag_byte_candidates)}')

# Try: same key for all bytes in a short sequence
print()
print('Looking for CHAKRA{ with same key for all chars...')
for key in range(256):
    for off in range(0x200, size - 50):
        if raw[off] ^ key == ord('C'):
            candidate = bytes(b ^ key for b in raw[off:off+7])
            if candidate == b'CHAKRA{':
                end = off + 7
                result = [chr(raw[off+i] ^ key) for i in range(7)]
                # Continue to find the flag
                flag = 'CHAKRA{'
                for i in range(7, 60):
                    if off + i >= size:
                        break
                    c = raw[off+i] ^ key
                    if chr(c) == '}':
                        flag += '}'
                        break
                    if chr(c) in valid_flag_chars:
                        flag += chr(c)
                    else:
                        break
                if len(flag) > 10 and '}' in flag:
                    print(f'  key=0x{key:02x} off=0x{off:x}: {flag}')
