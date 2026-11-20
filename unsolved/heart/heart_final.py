#!/usr/bin/env python3
"""
Final approach: Re-read the challenge description very carefully.

"The confession was never stored in one place. It lives as a chain of
little notes in the heap, each masked so a casual glance sees nothing,
linked by pointers into an address space that no longer exists."

"Plenty of feelings in there are lies. Only one chain is the truth."

The SECOND CHAKRA string says: "th3_r34l_0n3_1s_x0r3d_p3r_n0d3"
= "the real one is xored per node"

This tells us the REAL FLAG is XOR'd. Each node has one character XOR'd with 
the node's address (or some per-node key).

The DECOYS are in plaintext. The two we found ARE the decoys.

Now, the file has 109424 bytes. The header occupies some bytes.
Let me check: what comes right after the header text?

The header text ends at offset 0x1D0 roughly (after "note: nodes are LOVE-tagged...").
After that, there's binary data.

KEY INSIGHT: "HEARTLIST=0x555555458000" gives us the VA of the HEAD POINTER.
The HEAD POINTER'S VALUE is what we need. But it's stored at VA 0x555555458000
which maps to file offset 0x58000 > file size.

UNLESS: the file offset mapping is NOT (VA - image_base).
What if image_base is the base of the executable TEXT section,
but the HEAP is at a different base address?

The heap base could be: 0x555555458000 - some_heap_offset

Actually, for Linux processes with ASLR disabled (pid=1337 suggests a toy program),
the heap might be at a predictable location. Let's check:
- Stack of 64-bit programs grows from high addresses
- Heap starts just after BSS segment
- image_base=0x555555400000, heap might start at 0x555555600000 or similar

Alternative: The file might encode the heap starting from address 0x555555458000.
But then HEARTLIST VA 0x555555458000 = file offset 0x0000,
and the head pointer value is at file[0:8]:
0xC187A37477A5CFE7 (first 8 bytes of file)

That's clearly encrypted too. So the head pointer is masked!

What if the head pointer is XOR'd with HEARTLIST address?
Decrypted head = 0xC187A37477A5CFE7 XOR 0x555555458000 ... that's 32-bit XOR, not right.

Let me try XOR with full VA:
0xC187A37477A5CFE7 XOR 0x555555458000 = ???
Actually the mask might be just the lower bits.

Let me look at this from the perspective of the NODE STRUCTURE.
A typical linked list node in C:
struct Node {
    uint64_t next;      // pointer to next node
    uint64_t key;       // XOR key for data
    uint8_t  data[];    // masked character(s)
};

Or maybe the key IS the address:
masked_char = real_char XOR (node_va & 0xFF)  // low byte of address

For the decoy at offset 0x8000 (VA = image_base + 0x8000 = 0x555555408000):
CHAKRA{str1ngs_w0nt_s4v3_y0u}
If this is XOR'd with 0x00 (VA low byte) = plaintext. YES! 0x00 XOR anything = anything.
Low byte of 0x555555408000 = 0x00. So the decoy IS at an address ending in 0x00 -> no XOR.

For the second CHAKRA at offset 0x9800 (VA = 0x555555409800):
Low byte = 0x00 again. Also plaintext.

Real flag nodes must be at addresses where the low byte != 0.

So the scheme is: char XOR (node_va & 0xFF) = stored_masked_char.
We need to find nodes where stored ^ (va & 0xFF) gives printable CHAKRA{...} text.

Let me scan for this!
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

size = len(raw)
image_base = 0x555555400000

# Scan every byte offset in the file
# For each offset, compute: decrypted = raw[off] XOR (low_byte_of_VA)
# VA = image_base + off
# Low byte = (image_base + off) & 0xFF
# = (0x00 + off) & 0xFF  (since image_base ends in 0x000000)
# = off & 0xFF

# So: decrypted[off] = raw[off] XOR (off & 0xFF)

decrypted = bytearray(size)
for i in range(size):
    decrypted[i] = raw[i] ^ (i & 0xFF)

# Search for CHAKRA{ in decrypted
print('=== Searching for CHAKRA{ with key=(off & 0xFF) ===')
idx = 0
while True:
    idx = bytes(decrypted).find(b'CHAKRA{', idx)
    if idx == -1:
        break
    flag_end = bytes(decrypted).find(b'}', idx)
    if flag_end != -1 and flag_end - idx < 80:
        print(f'  Found at offset 0x{idx:x}: {decrypted[idx:flag_end+1].decode(errors="replace")}')
    idx += 1

# Also try with 2-byte key: (off & 0xFFFF)
print()
print('=== Searching with key=(off & 0xFFFF) / 16-bit ===')
decrypted16 = bytearray(size)
for i in range(size - 1):
    key16 = i & 0xFFFF
    decrypted16[i] = raw[i] ^ (key16 & 0xFF)
    if i + 1 < size:
        decrypted16[i+1] = raw[i+1] ^ ((key16 >> 8) & 0xFF)

idx = 0
while True:
    idx = bytes(decrypted16).find(b'CHAKRA{', idx)
    if idx == -1:
        break
    print(f'  Found at 0x{idx:x}: {decrypted16[idx:idx+50]}')
    idx += 1

# Try with VA bits approach: key = (VA >> 3) & 0xFF
print()
print('=== Searching with key=((image_base+off)>>3)&0xFF ===')
decrypted_v2 = bytearray(size)
for i in range(size):
    va = image_base + i
    key = (va >> 3) & 0xFF
    decrypted_v2[i] = raw[i] ^ key

idx = 0
while True:
    idx = bytes(decrypted_v2).find(b'CHAKRA{', idx)
    if idx == -1:
        break
    end = bytes(decrypted_v2).find(b'}', idx)
    if end != -1 and end - idx < 80:
        print(f'  Found at 0x{idx:x}: {decrypted_v2[idx:end+1].decode(errors="replace")}')
    idx += 1

# Most importantly: the KEY insight from the clue "x0r3d_p3r_n0d3"
# Each NODE has its OWN key. Not per-byte.
# A node = one chunk of data. The key applies to the WHOLE node.
# 
# What IS a node? Probably a struct with fixed size.
# Let's try NODE_SIZE = 8 (each node holds 1 char, key = node index?)
print()
print('=== Try node-based XOR: each 8-byte node, key = node_number ===')
NODE_SIZE = 8
header_end = 0x200

result = []
for node_idx in range(size // NODE_SIZE):
    off = node_idx * NODE_SIZE
    if off < header_end:
        continue
    node_key = node_idx  # simplest hypothesis
    node_bytes = raw[off:off+NODE_SIZE]
    decrypted_node = bytes(b ^ (node_key & 0xFF) for b in node_bytes)
    result.append((off, node_key, decrypted_node))

# Find nodes that decode to printable
printable_nodes = [(off, key, dec) for off, key, dec in result 
                   if all(0x20 <= b < 0x7f or b == 0 for b in dec)]
print(f'Printable nodes: {len(printable_nodes)} out of {len(result)}')

# Look for CHAKRA characters among them
chakra_chars = set('CHAKRchakr{}0123456789_abcdefghijklmnopqrstuvwxyz')
for off, key, dec in printable_nodes[:20]:
    print(f'  off=0x{off:06x} key={key}: {dec}')
