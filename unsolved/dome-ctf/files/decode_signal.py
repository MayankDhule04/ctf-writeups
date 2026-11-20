import numpy as np, colorsys, itertools, re
from PIL import Image
from scipy import ndimage

p = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421.jpg"
arr = np.array(Image.open(p).convert("RGB"))
h, w, _ = arr.shape
bg = np.median(arr, axis=1)
diff = np.abs(arr.astype(int) - bg[:, None, :].astype(int)).sum(axis=2)
mask = diff > 40
labeled, num = ndimage.label(mask)

blobs = []
for i in range(1, num+1):
    ys, xs = np.where(labeled == i)
    if len(xs) < 300:
        continue
    cols = arr[ys, xs]
    uniq, cnt = np.unique(cols.reshape(-1,3), axis=0, return_counts=True)
    dom = uniq[cnt.argmax()]
    cx, cy = xs.mean(), ys.mean()
    bw = xs.max()-xs.min()+1; bh = ys.max()-ys.min()+1
    r,g,b = [int(c) for c in dom]
    hh,ss,vv = colorsys.rgb_to_hsv(r/255,g/255,b/255)
    blobs.append(dict(cx=cx, cy=cy, rgb=(r,g,b), hue=hh*360, sat=ss, val=vv,
                      w=bw, h=bh, area=len(xs)))

print("blobs:", len(blobs))

def letters_from(seq_vals, lo=0, hi=360, n=26, base='A'):
    out = ""
    for v in seq_vals:
        idx = int((v-lo)/(hi-lo)*n) % n
        out += chr(ord(base)+idx)
    return out

orders = {
    "by_y": sorted(blobs, key=lambda b:(b['cy'], b['cx'])),
    "by_x": sorted(blobs, key=lambda b:(b['cx'], b['cy'])),
    "rowmajor": sorted(blobs, key=lambda b:(round(b['cy']/200), b['cx'])),
    "colmajor": sorted(blobs, key=lambda b:(round(b['cx']/200), b['cy'])),
    "by_hue": sorted(blobs, key=lambda b:b['hue']),
}

print("\n=== hue->A-Z (26) for each order ===")
for name, seq in orders.items():
    print(f"{name:10}:", letters_from([b['hue'] for b in seq]))

print("\n=== hue->0-15 hex nibbles -> bytes ===")
for name, seq in orders.items():
    nib = [int(b['hue']/360*16)%16 for b in seq]
    hx = "".join("%x"%n for n in nib)
    try:
        bs = bytes.fromhex(hx) if len(hx)%2==0 else b""
        txt = "".join(chr(c) if 32<=c<127 else "." for c in bs)
    except Exception:
        txt=""
    print(f"{name:10}: {hx}  ascii={txt}")

print("\n=== dominant-channel idea: R,G,B as ascii per blob ===")
for name, seq in orders.items():
    s="".join(chr(b['rgb'][0]) if 32<=b['rgb'][0]<127 else '.' for b in seq)
    print(f"{name:10} R:", s)

# nearest CSS-ish named color first-letter
named = {
 'red':(255,0,0),'green':(0,128,0),'lime':(0,255,0),'blue':(0,0,255),'yellow':(255,255,0),
 'cyan':(0,255,255),'magenta':(255,0,255),'orange':(255,165,0),'purple':(128,0,128),
 'pink':(255,192,203),'teal':(0,128,128),'violet':(238,130,238),'olive':(128,128,0),
 'navy':(0,0,128),'maroon':(128,0,0),'gold':(255,215,0),'indigo':(75,0,130),
 'turquoise':(64,224,208),'tan':(210,180,140),'salmon':(250,128,114),'orchid':(218,112,214),
 'skyblue':(135,206,235),'springgreen':(0,255,127),'lavender':(230,230,250)
}
def nearest(rgb):
    best=None;bd=1e9
    for nm,c in named.items():
        d=sum((a-b)**2 for a,b in zip(rgb,c))
        if d<bd:bd=d;best=nm
    return best
print("\n=== nearest named color first letters ===")
for name, seq in orders.items():
    nms=[nearest(b['rgb']) for b in seq]
    print(f"{name:10}:", "".join(n[0].upper() for n in nms), "|", ",".join(nms))
