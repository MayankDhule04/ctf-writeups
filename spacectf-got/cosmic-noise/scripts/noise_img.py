#!/usr/bin/env python3
import wave, struct
w=wave.open("/work/noise.wav"); n=w.getnframes()
u=[x & 0xFFFF for x in struct.unpack("<%dh"%n, w.readframes(n))]
from PIL import Image
def render(bits, side, name):
    img=Image.new("1",(side,side)); px=img.load()
    for i in range(side*side):
        px[i%side,i//side]=bits[i] if i<len(bits) else 0
    sc=max(1,420//side)
    img.resize((side*sc,side*sc),Image.NEAREST).save(f"/work/start_{name}.png")
for bit,bn in ((0,"LSB"),(15,"MSB"),(1,"b1"),(14,"b14")):
    bits=[(x>>bit)&1 for x in u]
    for side in (64,89,100,128,160,177,200,256):
        render(bits, side, f"{bn}_{side}")
print("done")
