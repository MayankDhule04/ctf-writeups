#!/usr/bin/env python3
import re, ast, numpy as np
from PIL import Image
import zxingcpp
D7 = open("/work/flashback_scripts/scripts/__Packages/D7.as").read()
def arr(fn):
    m = re.search(r"static function "+fn+r"\(\)\s*\{\s*return (\[.*?\]);\s*\}", D7, re.S)
    return ast.literal_eval(m.group(1))
q2=arr("c"); q3=arr("d"); SIZE=89
def decode(level):
    seed=q2[level]%2147483647
    if seed<=0: seed=1
    enc=q3[level]; q4=[]
    for i in range(len(enc)):
        seed=seed*48271%2147483647; q4.append(enc[i]^(seed%65536))
    return np.array([[ (q4[(y*SIZE+x)//16]>>(15-((y*SIZE+x)%16)))&1 for x in range(SIZE)] for y in range(SIZE)],dtype=np.uint8)
L=[decode(i) for i in range(len(q3))]
U=np.zeros((SIZE,SIZE),np.uint8)
for m in L: U|=m   # ON = dark module

FINDER=np.array([
[1,1,1,1,1,1,1],
[1,0,0,0,0,0,1],
[1,0,1,1,1,0,1],
[1,0,1,1,1,0,1],
[1,0,1,1,1,0,1],
[1,0,0,0,0,0,1],
[1,1,1,1,1,1,1]],np.uint8)

def place_finders(M):
    M=M.copy()
    # TL
    M[0:7,0:7]=FINDER; M[0:8,7]=0; M[7,0:8]=0
    # TR
    M[0:7,SIZE-7:SIZE]=FINDER; M[0:8,SIZE-8]=0; M[7,SIZE-8:SIZE]=0
    # BL
    M[SIZE-7:SIZE,0:7]=FINDER; M[SIZE-8:SIZE,7]=0; M[SIZE-8,0:8]=0
    # dark module (for version V): ( (4V+9), 8 ) -> V=18 -> (81,8)
    M[4*18+9,8]=1
    return M

def to_img(mat,scale=10,qz=10):
    big=np.where(mat==1,0,255).astype(np.uint8)  # dark module(1)->black
    big=np.kron(big,np.ones((scale,scale),np.uint8))
    big=np.pad(big,qz*scale,constant_values=255)
    return Image.fromarray(big,"L")

cands={"union_raw":U,"union_finders":place_finders(U)}
found=False
for name,M in cands.items():
    for inv in (False,True):
        MM=(1-M) if inv else M
        for rot in range(4):
            r=np.rot90(MM,rot)
            img=to_img(r)
            if name=="union_finders" and inv==False and rot==0:
                img.save("/work/fb_qr_final.png")
            for res in zxingcpp.read_barcodes(img):
                print(f"DECODED [{name} inv={inv} rot={rot}]: {res.text!r}")
                found=True
if not found: print("still no decode")
