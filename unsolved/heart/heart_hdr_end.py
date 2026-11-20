#!/usr/bin/env python3
"""Look at exact bytes right after the header text ends."""
import struct

with open('heart.dmp', 'rb') as f:
    raw = f.read()

# Find the end of the header text by locating "lie.\n" (last line of text)
hdr_end_marker = b'lie.\n'
hdr_end = raw.find(hdr_end_marker)
if hdr_end == -1:
    hdr_end_marker = b'lie.'
    hdr_end = raw.find(hdr_end_marker)

print(f'Header text ends at offset: 0x{hdr_end:x} + {len(hdr_end_marker)} = 0x{hdr_end + len(hdr_end_marker):x}')
data_start = hdr_end + len(hdr_end_marker)
print(f'Data region starts at: 0x{data_start:x}')
print()

# Show first 256 bytes of data region in detail
print('=== First 512 bytes of data region ===')
for off in range(data_start, min(data_start + 512, len(raw)), 8):
    val = struct.unpack_from('<Q', raw, off)[0]
    text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
    print(f'  0x{off:06x}: {val:016x}  {text}')

print()
# The header says: "note: the confession list head pointer follows"
# Then: "HEARTLIST=0x555555458000"
# Maybe after the header, the first 8 bytes ARE the head pointer (masked or not)!
head_ptr_off = data_start
head_ptr = struct.unpack_from('<Q', raw, head_ptr_off)[0]
print(f'First 8 bytes after header: 0x{head_ptr:016x}')
print()

# Try interpreting these 8 bytes as an XOR-masked pointer
# If XOR'd with HEARTLIST VA:
heartlist_va = 0x555555458000
image_base = 0x555555400000
xored_with_heartlist = head_ptr ^ heartlist_va
print(f'XOR with HEARTLIST VA: 0x{xored_with_heartlist:016x}')
xored_with_base = head_ptr ^ image_base
print(f'XOR with image_base: 0x{xored_with_base:016x}')
print()

# Maybe the mask = low 32 bits of the VA address itself
# Let's try: if data starts at VA = image_base + data_start
# Then mask = (image_base + data_start) & 0xFFFFFFFF
mask_lo32 = (image_base + data_start) & 0xFFFFFFFF
unmasked = head_ptr ^ (mask_lo32 | (mask_lo32 << 32))
print(f'XOR with lo32 repeated: 0x{unmasked:016x}')
print()

# Try all 4-byte XOR keys to see which gives a valid VA
print('Trying 4-byte XOR keys that make first 8 bytes a valid VA...')
for key32 in range(0x0000, 0x10000, 1):
    key = key32 | (key32 << 16) | (key32 << 32) | (key32 << 48)
    unmasked = head_ptr ^ key
    if 0x555555400000 <= unmasked <= 0x555555600000:
        off = unmasked - image_base
        print(f'  key=0x{key32:04x}: VA=0x{unmasked:x} offset=0x{off:x}')

# Check the "note: the confession list head pointer follows" text
# Maybe what IMMEDIATELY follows that text IS the head pointer
note_text = b'note: the confession list head pointer follows\n'
note_pos = raw.find(note_text)
if note_pos != -1:
    after_note = note_pos + len(note_text)
    print(f'\nText "head pointer follows" at 0x{note_pos:x}')
    print(f'Bytes immediately after:')
    for off in range(after_note, after_note + 64, 8):
        val = struct.unpack_from('<Q', raw, off)[0]
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
        print(f'  0x{off:06x}: {val:016x}  {text}')

# Check what comes after HEARTLIST=... line
heartlist_line = b'HEARTLIST=0x555555458000\n'
hl_pos = raw.find(heartlist_line)
if hl_pos != -1:
    after_hl = hl_pos + len(heartlist_line)
    print(f'\n"HEARTLIST=..." line at 0x{hl_pos:x}')
    print(f'Bytes immediately after:')
    for off in range(after_hl, after_hl + 128, 8):
        val = struct.unpack_from('<Q', raw, off)[0]
        text = ''.join(chr(b) if 0x20<=b<0x7f else '.' for b in raw[off:off+8])
        print(f'  0x{off:06x}: {val:016x}  {text}')
