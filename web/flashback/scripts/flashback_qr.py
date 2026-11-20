#!/usr/bin/env python3
import re, ast
D7 = open("/work/flashback_scripts/scripts/__Packages/D7.as").read()
def arr(fn):
    m = re.search(r"static function "+fn+r"\(\)\s*\{\s*return (\[.*?\]);\s*\}", D7, re.S)
    return ast.literal_eval(m.group(1))
q2 = arr("c"); q3 = arr("d")
SIZE=89
from PIL import Image

def decode(level):
    seed=q2[level]%2147483647
    if seed<=0: seed=1
    enc=q3[level]; q4=[]
    for i in range(len(enc)):
        seed=seed*48271%2147483647
        q4.append(enc[i]^(seed%65536))
    return [(q4[(y*SIZE+x)//16]>>(15-((y*SIZE+x)%16)))&1 for y in range(SIZE) for x in range(SIZE)]

L=[decode(i) for i in range(len(q3))]
union=[1 if any(L[k][i] for k in range(5)) else 0 for i in range(SIZE*SIZE)]

def build(matrix_on_is_dark, invert):
    QZ=6; scale=8
    W=(SIZE+2*QZ)
    img=Image.new("L",(W,W),255)
    px=img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            on=matrix_on_is_dark[y*SIZE+x]
            if invert: on=1-on
            px[x+QZ,y+QZ]= 0 if on else 255
    img=img.resize((W*scale,W*scale),Image.NEAREST)
    return img

for inv in (0,1):
    img=build(union,inv)
    img.save(f"/work/fb_qr_{'inv' if inv else 'norm'}.png")

# decode attempts
results=[]
try:
    import cv2, numpy as np
    det=cv2.QRCodeDetector()
    for inv in (0,1):
        im=cv2.imread(f"/work/fb_qr_{'inv' if inv else 'norm'}.png",cv2.IMREAD_GRAYSCALE)
        d,pts,_=det.detectAndDecode(im)
        results.append(("cv2 inv="+str(inv), d))
except Exception as e:
    results.append(("cv2 error", str(e)))
try:
    from pyzbar.pyzbar import decode as zdec
    for inv in (0,1):
        im=Image.open(f"/work/fb_qr_{'inv' if inv else 'norm'}.png")
        r=zdec(im)
        results.append(("zbar inv="+str(inv), [x.data for x in r]))
except Exception as e:
    results.append(("zbar error", str(e)))

for name,r in results:
    print(name, "->", r)
