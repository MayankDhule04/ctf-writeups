import numpy as np
from PIL import Image
from scipy import ndimage

p = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421.jpg"
im = Image.open(p).convert("RGB")
arr = np.array(im)
h, w, _ = arr.shape
print("image shape:", arr.shape)

# background is a vertical gradient of blue tones (low saturation-ish blueish).
# Identify background per-row by taking median color per row, then find pixels
# that deviate significantly from that row's background.
bg_per_row = np.median(arr, axis=1)  # (h,3)

diff = np.abs(arr.astype(int) - bg_per_row[:, None, :].astype(int)).sum(axis=2)
mask = diff > 40  # threshold

labeled, num = ndimage.label(mask)
print("num blobs:", num)

blobs = []
for i in range(1, num+1):
    ys, xs = np.where(labeled == i)
    if len(xs) < 20:
        continue
    cx, cy = xs.mean(), ys.mean()
    colors = arr[ys, xs]
    # most common color (mode)
    uniq, counts = np.unique(colors.reshape(-1,3), axis=0, return_counts=True)
    dom = uniq[counts.argmax()]
    area = len(xs)
    w_box = xs.max()-xs.min()+1
    h_box = ys.max()-ys.min()+1
    blobs.append((cx, cy, tuple(int(c) for c in dom), area, w_box, h_box))

blobs.sort(key=lambda b: (b[1], b[0]))
print("num significant blobs:", len(blobs))
for b in blobs:
    print(f"cx={b[0]:.1f} cy={b[1]:.1f} color=rgb{b[2]} hex=#{b[2][0]:02x}{b[2][1]:02x}{b[2][2]:02x} area={b[3]} w={b[4]} h={b[5]}")
