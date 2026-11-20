#!/usr/bin/env python3
"""
Reverse engineer the node structure in heart.dmp.

Key facts:
- "nodes are LOVE-tagged" - LOVE appears somewhere
- "each masked" - XOR'd
- "linked by pointers" - next ptr in each node
- "Only one chain is the truth" - multiple chains, one correct
- 2 decoy CHAKRA strings at 0x8000, 0x9800 (plaintext - these are LIES)
- Real flag is XOR'd per node

Strategy: The LOVE tag on each node is 4 bytes that become readable after XOR.
But wait - the header says nodes are LOVE-tagged, and "the freed ones lie."
The DECOY CHAKRAs at 0x8000 and 0x9800 are in plaintext.
Maybe "LOVE-tagged" means the node starts with 0x4C4F5645 (LOVE in ASCII).
If XOR masked: the raw bytes XOR key = the stored bytes XOR 0x4C4F5645.

Let's look at the data just before the CHAKRA strings.
The decoy at 0x8000 is 30 bytes: "CHAKRA{str1ngs_w0nt_s4v3_y0u}"
A node might be: [4-byte tag] [8-byte next ptr] [1-byte key?] [data]

Actually: if the node starts with "LOVE" (4 bytes), and is XOR'd with a per-node key,
then bytes at offset N XOR key = the plaintext node.

Let's scan the file for all 4-byte sequences that would XOR to "LOVE":
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000

# "LOVE" = 0x4C 0x4F 0x56 0x45
LOVE = b'LOVE'

# Approach 1: Find what XOR key makes bytes at each position produce "LOVE"
# If raw[off:off+4] XOR key4 = LOVE, then key4 = raw[off:off+4] XOR LOVE

# But we need a consistent structure.
# 
# Alternative approach: The description says the true chain is the ONE real chain.
# The "lies" are freed nodes. The pointer chain for the real one terminates properly.
#
# Let me look at the file as containing N nodes of some fixed size,
# then try to figure out the size and structure.
#
# The file is 0x1AB70 = 109424 bytes.
# After header (~0x200 bytes), remaining = 109424 - 512 = 108912 bytes.
# 108912 / 32 = 3403 nodes of 32 bytes each?
# 108912 / 64 = 1701 nodes of 64 bytes each?
# 108912 / 48 = 2269 nodes of 48 bytes each?
#
# But the CHAKRA decoy at 0x8000 is 30 bytes + continuation...
# Node might be 64 bytes starting at 0x8000?
#
# Let me check what the structure looks like if nodes are 64 bytes,
# and the "LOVE" tag starts each node:

NODE_SIZE = 64  # hypothesis

print(f'=== Hypothesis: {NODE_SIZE}-byte nodes starting at 0x0200 ===')
header_end = 0x200
num_nodes = (size - header_end) // NODE_SIZE
print(f'Would give {num_nodes} nodes')

# For each node, try to find what single-byte XOR key makes the first 4 bytes = "LOVE"
# That won't work for a 4-byte key...
# 
# Actually, let me try: what if the XOR key is derived from the node address (VA)?
# "each masked" per node = f(address) XOR plaintext
# 
# Let's try: key = VA & 0xFF (low byte of address)
# Node at file offset 0x8000 has VA = 0x555555408000
# Low byte = 0x00
# XOR with 0x00 = identity, so "CHAKRA{...}" IS the node content (decoy is plaintext)

# REAL nodes must use a different key.
# The challenge says "walk what remains of its heart" - follow pointers.
# "linked by pointers into an address space that no longer exists"
# 
# What if the pointers ARE in the raw file but the VA-subtraction gives offsets
# that are within the file? Let me re-check the VA space.
#
# File = 0x1AB70 bytes. If image_base = 0x555555400000:
# Max VA in file = 0x555555400000 + 0x1AB70 = 0x5555554 1AB70
# = 0x5555 5541 AB70
#
# But HEARTLIST = 0x555555458000 > max VA in file!
# Unless... the dump doesn't start at image_base?
#
# What if the dump represents the heap starting at a DIFFERENT offset?
# E.g., "image_base=0x555555400000" is the base of the executable,
# but the heap starts higher. The dump might be of just the heap region.
#
# heap_start_va = some value where the file offset 0 corresponds to
# Let's try: the dump is of memory starting at 0x555555458000 (HEARTLIST)
# Then file offset 0 = VA 0x555555458000

# If that's the case, the HEARTLIST value stored at HEARTLIST is:
# raw[0:8] = first 8 bytes of file
first8 = struct.unpack_from('<Q', raw, 0)[0]
print(f'\nIf file starts at HEARTLIST VA 0x555555458000:')
print(f'  First 8 bytes as u64: 0x{first8:016x}')
alt_image_base = 0x555555458000
alt_chakra1_off = 0x555555408000 - alt_image_base  # Would be negative! (-0x50000)
print(f'  CHAKRA decoy would be at offset 0x{0x555555408000 - alt_image_base:x} (negative?)')

# That doesn't work either.
# 
# NEW IDEA: The dump file offset simply = VA - image_base for VAs IN the file.
# The HEARTLIST pointer at VA 0x555555458000 is OUT OF the file range,
# meaning it's not dumped. But the POINTER VALUE stored at HEARTLIST might
# point to nodes that ARE in the file.
#
# So HEARTLIST is a variable stored at VA 0x555555458000 (not in file),
# but its VALUE (the head node pointer) should point INTO the heap region 
# that IS in the file.
#
# We need to find nodes without knowing the head pointer.
# Strategy: Scan for all valid 64-bit values that, when used as VAs,
# point to offsets within the file AND those offsets also contain valid VAs.
# That's a "pointer chain" in the file.

print()
print('=== Scanning for XOR-masked pointer chains ===')
# If nodes have structure: [mask:u64] [masked_next:u64] [masked_data:N bytes]
# And unmasked_next = masked_next XOR mask
# Then unmasked_next should be a valid VA (in 0x555555400000..0x5555554_1AB70)

VA_LO = image_base
VA_HI = image_base + size

found_chains = []

for off in range(0x200, size - 16, 8):
    mask = struct.unpack_from('<Q', raw, off)[0]
    if mask == 0:
        continue
    masked_next = struct.unpack_from('<Q', raw, off + 8)[0]
    unmasked_next = masked_next ^ mask
    
    if VA_LO <= unmasked_next < VA_HI:
        next_off = unmasked_next - VA_LO
        # Verify the next node also has a valid structure
        if next_off + 16 <= size:
            next_mask = struct.unpack_from('<Q', raw, next_off)[0]
            next_masked_next = struct.unpack_from('<Q', raw, next_off + 8)[0]
            next_next = next_masked_next ^ next_mask
            
            if VA_LO <= next_next < VA_HI or next_next == 0:
                found_chains.append((off, mask, unmasked_next, next_off))

print(f'Found {len(found_chains)} potential chain links')
for i, (off, mask, next_va, next_off) in enumerate(found_chains[:30]):
    print(f'  [{i}] off=0x{off:x} mask=0x{mask:016x} next_va=0x{next_va:x} next_off=0x{next_off:x}')
