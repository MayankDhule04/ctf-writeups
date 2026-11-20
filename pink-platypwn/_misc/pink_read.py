#!/usr/bin/env python3
"""Enhanced fragment reading for DDS 002 (fragment 2) and DDS 006 (fragment 6).
Multiple processing: red-only, inverted, per-channel, edge-enhanced."""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Fragment 2: DDS 002 (1000x500 white bg with red handwriting)
im2 = Image.open('pink_hq/view/dds_002.png').convert('RGBA')
a2 = np.array(im2)
# The red text is in the left portion. Crop text region (approx 50-350, 100-350)
# Actually from the earlier view, text was at roughly left-center
r,g,b,al = a2[:,:,0].astype(int),a2[:,:,1].astype(int),a2[:,:,2].astype(int),a2[:,:,3]
red_mask = (r>120)&(g<100)&(b<100)&(al>128)
ys,xs = np.where(red_mask)
if len(ys):
    y0,y1,x0,x1 = max(0,ys.min()-10), min(im2.height,ys.max()+10), max(0,xs.min()-10), min(im2.width,xs.max()+10)
    # Crop and upscale
    crop = im2.crop((x0,y0,x1,y1))
    # Red channel only on white bg
    ca = np.array(crop.convert('RGBA'))
    red_only = np.ones_like(ca)*255
    rmask = (ca[:,:,0].astype(int)>120)&(ca[:,:,1].astype(int)<100)&(ca[:,:,2].astype(int)<100)
    red_only[rmask] = [0,0,0,255]  # black text on white
    red_only[:,:,3] = 255
    out = Image.fromarray(red_only.astype(np.uint8)).resize((crop.width*8, crop.height*8), Image.NEAREST)
    out.save('pink_hq/view/frag2_clean.png')
    print(f'Fragment 2: crop ({x0},{y0})-({x1},{y1}), saved frag2_clean.png')

# Fragment 6: DDS 006 (400x400 blue room, tiny white label bottom-right)
im6 = Image.open('pink_hq/view/dds_006.png').convert('RGBA')
a6 = np.array(im6)
# Find the white label region (bright pixels on blue bg)
r6,g6,b6,al6 = a6[:,:,0].astype(int),a6[:,:,1].astype(int),a6[:,:,2].astype(int),a6[:,:,3]
white_mask = (r6>200)&(g6>200)&(b6>200)&(al6>128)
ys6,xs6 = np.where(white_mask)
if len(ys6):
    y0,y1,x0,x1 = max(0,ys6.min()-5), min(im6.height,ys6.max()+5), max(0,xs6.min()-5), min(im6.width,xs6.max()+5)
    label = im6.crop((x0,y0,x1,y1))
    # Upscale a LOT (the label is ~20x15 pixels)
    big = label.resize((label.width*12, label.height*12), Image.NEAREST)
    big.save('pink_hq/view/frag6_nearest.png')
    # Also with bicubic for smoothing
    big2 = label.resize((label.width*12, label.height*12), Image.BICUBIC)
    ImageEnhance.Contrast(big2).enhance(3.0).save('pink_hq/view/frag6_smooth.png')
    # Invert
    inv = np.array(big.convert('RGB'))
    inv = 255 - inv
    Image.fromarray(inv).save('pink_hq/view/frag6_inverted.png')
    # Also rotate 180 (in case text is upside down)
    big.rotate(180).save('pink_hq/view/frag6_rot180.png')
    print(f'Fragment 6: label crop ({x0},{y0})-({x1},{y1}) size={label.size}, saved frag6 variants')
