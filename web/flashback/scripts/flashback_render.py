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
    seed = q2[level] % 2147483647
    if seed<=0: seed=1
    enc=q3[level]; q4=[]
    for i in range(len(enc)):
        seed = seed*48271 % 2147483647
        q4.append(enc[i] ^ (seed % 65536))
    return [ (q4[(y*SIZE+x)//16] >> (15-((y*SIZE+x)%16))) & 1 for y in range(SIZE) for x in range(SIZE)]

L=[decode(i) for i in range(len(q3))]
N=SIZE*SIZE
colors=[(255,60,60),(60,200,60),(80,120,255),(255,200,40),(220,60,220)]
img=Image.new("RGB",(SIZE,SIZE),(0,0,0)); px=img.load()
for y in range(SIZE):
    for x in range(SIZE):
        i=y*SIZE+x
        s=[k for k in range(5) if L[k][i]]
        if len(s)==1: px[x,y]=colors[s[0]]
        elif len(s)>1:
            r=sum(colors[k][0] for k in s)//len(s); g=sum(colors[k][1] for k in s)//len(s); b=sum(colors[k][2] for k in s)//len(s)
            px[x,y]=(r,g,b)
img.resize((SIZE*8,SIZE*8),Image.NEAREST).save("/work/fb_color.png")

# per-level count overlap distribution
from collections import Counter
cnt=Counter(sum(L[k][i] for k in range(5)) for i in range(N))
print("overlap counts (how many levels set each pixel):", dict(sorted(cnt.items())))
print("done")
