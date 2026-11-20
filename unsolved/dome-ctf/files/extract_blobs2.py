import numpy as np
from PIL import Image
from scipy import ndimage

p = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421.jpg"
im = Image.open(p).convert("RGB")
arr = np.array(im)
h, w, _ = arr.shape

bg_per_row = np.median(arr, axis=1)
diff = np.abs(arr.astype(int) - bg_per_row[:, None, :].astype(int)).sum(axis=2)
mask = diff > 40

labeled, num = ndimage.label(mask)

results = []
for i in range(1, num+1):
    ys, xs = np.where(labeled == i)
    if len(xs) < 20:
        continue
    colors = arr[ys, xs].astype(int)
    uniq, counts = np.unique(colors.reshape(-1,3), axis=0, return_counts=True)
    # if there are two very different dominant colors with substantial counts, split
    # sort by count desc
    order = np.argsort(-counts)
    uniq = uniq[order]; counts = counts[order]
    # cluster colors: greedily group colors within distance 30 of a cluster center
    clusters = []  # list of (center, total_count, pixel_indices mask)
    assigned = np.zeros(len(xs), dtype=int) - 1
    centers = []
    for ci in range(len(uniq)):
        c = uniq[ci]
        # find existing cluster center close to this color
        found = -1
        for k, cen in enumerate(centers):
            if np.abs(cen.astype(int)-c.astype(int)).sum() < 60:
                found = k
                break
        if found == -1:
            centers.append(c)
            found = len(centers)-1
        # assign pixels matching this exact color to this cluster
        matches = np.all(colors == c, axis=1)
        assigned[matches] = found

    for k, cen in enumerate(centers):
        sel = assigned == k
        if sel.sum() < 20:
            continue
        cxs = xs[sel]; cys = ys[sel]
        cx, cy = cxs.mean(), cys.mean()
        bw = cxs.max()-cxs.min()+1
        bh = cys.max()-cys.min()+1
        results.append((cx, cy, tuple(int(v) for v in cen), sel.sum(), bw, bh))

results.sort(key=lambda r: (r[1], r[0]))
print("total clustered blobs:", len(results))
for r in results:
    print(f"cx={r[0]:7.1f} cy={r[1]:7.1f} rgb={r[2]} hex=#{r[2][0]:02x}{r[2][1]:02x}{r[2][2]:02x} area={r[3]:6d} w={r[4]:4d} h={r[5]:4d}")
