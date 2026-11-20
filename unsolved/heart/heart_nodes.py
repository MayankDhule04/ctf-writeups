#!/usr/bin/env python3
"""
Heart dump node walker.

From the header:
  image_base = 0x555555400000
  HEARTLIST  = 0x555555458000  (head of linked list)
  "nodes are LOVE-tagged; the freed ones lie"
  "each masked so a casual glance sees nothing"
  "linked by pointers"
  "Only one chain is the truth"

The file is 109424 bytes.
image_base maps to file offset 0.
HEARTLIST = 0x555555458000 -> offset 0x58000 = 360448 which is > file size.

BUT: We found two CHAKRA strings at file offsets 0x8000 and 0x9800.
0x8000 + image_base = 0x555555408000 (VA of decoy)
0x9800 + image_base = 0x555555409800 (VA of second CHAKRA)

So file offset = VA - image_base works for the data region!
But HEARTLIST = 0x555555458000 -> offset 0x58000 which is beyond file.

The file only covers up to offset 0x1AB70. 
VAs covered: 0x555555400000 to 0x5555554 + 0x1AB70 = 0x55555541AB70

So HEARTLIST at 0x555555458000 is NOT in the file directly.
The head pointer VALUE (what HEARTLIST points to) might be IN the file.

Let me look at what's at offset 0x8000 more carefully — the decoy node.
If this is a proper linked list node, offset 0x8000 should have:
  - LOVE tag (4 bytes)
  - next pointer (8 bytes, VA)
  - XOR key (some bytes)
  - masked data (the actual character/word)

Let's look at bytes around 0x7FF0 (just before the CHAKRA text)
"""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

image_base = 0x555555400000

def va_to_off(va):
    return va - image_base

def off_to_va(off):
    return off + image_base

def read_u64(off):
    if 0 <= off <= len(raw) - 8:
        return struct.unpack_from('<Q', raw, off)[0]
    return None

def read_u32(off):
    if 0 <= off <= len(raw) - 4:
        return struct.unpack_from('<I', raw, off)[0]
    return None

# Look at a wide window around the decoy CHAKRA at 0x8000
print('=== Node region around offset 0x7D00-0x8100 ===')
for off in range(0x7D00, 0x8100, 8):
    val64 = read_u64(off)
    text = raw[off:off+8]
    printable = ''.join(chr(b) if 0x20 <= b < 0x7f else '.' for b in text)
    # Check if val64 looks like a VA in range
    is_va = (val64 is not None and 
             0x555555400000 <= val64 <= 0x555555600000)
    note = ' <- VA!' if is_va else ''
    print(f'  0x{off:06x}: {val64:016x}  {printable}{note}')

print()
print('=== Look for VA pointers anywhere in the dump ===')
va_min = 0x555555400000
va_max = 0x555555600000
va_refs = []
for off in range(0, len(raw) - 8, 8):
    val = struct.unpack_from('<Q', raw, off)[0]
    if va_min <= val <= va_max:
        target_off = va_to_off(val)
        va_refs.append((off, val, target_off))

print(f'Total VA-like 64-bit values: {len(va_refs)}')
for off, val, target_off in va_refs[:40]:
    target_in_file = 0 <= target_off < len(raw)
    target_text = ''
    if target_in_file:
        target_bytes = raw[target_off:target_off+8]
        target_text = ''.join(chr(b) if 0x20 <= b < 0x7f else '.' for b in target_bytes)
    print(f'  0x{off:06x}: VA=0x{val:016x} -> offset=0x{target_off:x} {"(in file: " + target_text + ")" if target_in_file else "(OUT OF FILE)"}')
