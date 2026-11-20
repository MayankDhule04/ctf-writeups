#!/usr/bin/env python3
"""PINK HQ — re-extract DDS with correct sizes, decode DXT1/DXT5, save as PNG.
Use offset of next signature (DDS or PNG) as the boundary for each DDS."""
import struct, os, re
from PIL import Image
import numpy as np

F = "pink_hq/PINK+_HQ.lim2"
d = open(F, 'rb').read()
json_len = struct.unpack('<I', d[4:8])[0]
blob = d[8+json_len:]

# Find all image offsets (both PNG and DDS)
png_sig = b'\x89PNG\r\n\x1a\n'
dds_sig = b'DDS '
all_offsets = []
pos = 0
while True:
    pi = blob.find(png_sig, pos)
    di = blob.find(dds_sig, pos)
    if pi == -1 and di == -1: break
    if pi == -1: nxt = di; typ = 'dds'
    elif di == -1: nxt = pi; typ = 'png'
    elif pi < di: nxt = pi; typ = 'png'
    else: nxt = di; typ = 'dds'
    all_offsets.append((nxt, typ))
    pos = nxt + 1
all_offsets.sort()
print(f"Total image signatures: {len(all_offsets)}")

os.makedirs('pink_hq/view', exist_ok=True)

def decode_dxt1_block(data):
    c0 = struct.unpack('<H', data[0:2])[0]
    c1 = struct.unpack('<H', data[2:4])[0]
    def rgb565(c):
        r = ((c >> 11) & 0x1F) * 255 // 31
        g = ((c >> 5) & 0x3F) * 255 // 63
        b = (c & 0x1F) * 255 // 31
        return (r, g, b, 255)
    p0 = rgb565(c0); p1 = rgb565(c1)
    if c0 > c1:
        p2 = tuple((2*a+b)//3 for a,b in zip(p0[:3],p1[:3]))+(255,)
        p3 = tuple((a+2*b)//3 for a,b in zip(p0[:3],p1[:3]))+(255,)
    else:
        p2 = tuple((a+b)//2 for a,b in zip(p0[:3],p1[:3]))+(255,)
        p3 = (0,0,0,0)
    pal = [p0, p1, p2, p3]
    bits = struct.unpack('<I', data[4:8])[0]
    pixels = []
    for i in range(16):
        idx = (bits >> (2*i)) & 3
        pixels.append(pal[idx])
    return pixels

def decode_dxt5_block(data):
    a0 = data[0]; a1 = data[1]
    alpha_bits = int.from_bytes(data[2:8], 'little')
    alphas = [a0, a1]
    if a0 > a1:
        for i in range(6): alphas.append((a0*(6-i) + a1*(1+i)) // 7)
    else:
        for i in range(4): alphas.append((a0*(4-i) + a1*(1+i)) // 5)
        alphas += [0, 255]
    alpha_vals = []
    for i in range(16):
        idx = (alpha_bits >> (3*i)) & 7
        alpha_vals.append(alphas[idx])
    color_pixels = decode_dxt1_block(data[8:16])
    return [(*cp[:3], av) for cp, av in zip(color_pixels, alpha_vals)]

def decode_dds(data):
    if data[:4] != b'DDS ': return None
    h = struct.unpack('<I', data[12:16])[0]
    w = struct.unpack('<I', data[16:20])[0]
    fourcc = data[84:88]
    bw = max(1, (w+3)//4); bh = max(1, (h+3)//4)
    img = np.zeros((h, w, 4), dtype=np.uint8)
    off = 128
    for by in range(bh):
        for bx in range(bw):
            if fourcc == b'DXT1':
                if off+8 > len(data): break
                pixels = decode_dxt1_block(data[off:off+8]); off += 8
            elif fourcc in (b'DXT5', b'DXT3'):
                if off+16 > len(data): break
                pixels = decode_dxt5_block(data[off:off+16]); off += 16
            else:
                return None
            for pi, px in enumerate(pixels):
                py_local = pi // 4; px_local = pi % 4
                y = by*4 + py_local; x = bx*4 + px_local
                if y < h and x < w:
                    img[y, x] = px
    return Image.fromarray(img)

for i, (off, typ) in enumerate(all_offsets):
    next_off = all_offsets[i+1][0] if i+1 < len(all_offsets) else len(blob)
    chunk = blob[off:next_off]
    fn = f'pink_hq/view/{typ}_{i:03d}.png'
    if typ == 'png':
        # Find IEND
        iend = chunk.find(b'IEND')
        if iend != -1:
            png_data = chunk[:iend+12]
            open(fn, 'wb').write(png_data)
    elif typ == 'dds':
        im = decode_dds(chunk)
        if im:
            im.save(fn)
            print(f"  DDS {i}: {im.size} -> {fn}")
        else:
            print(f"  DDS {i}: decode failed, fourcc={chunk[84:88]}")

print("done - all textures in pink_hq/view/")
