import colorsys

# cleaned list of 19 "real" blobs (merged one split using second pass), ordered as detected
blobs = [
(1097.5, 331.9, (62, 204, 218)),
(3421.0, 401.4, (142, 127, 222)),
(3682.4, 416.4, (254, 26, 233)),
(1797.9, 689.9, (3, 98, 208)),
(766.5, 1070.5, (161, 97, 113)),
(1330.1, 1279.0, (161, 11, 158)),
(3388.4, 1338.9, (145, 210, 250)),
(2353.1, 1365.4, (50, 238, 17)),
(3830.0, 1388.1, (4, 230, 94)),
(3454.5, 1440.5, (220, 193, 246)),
(2449.0, 1567.0, (227, 49, 159)),
(966.6, 1711.5, (6, 88, 24)),
(510.5, 1829.5, (213, 144, 102)),
(2573.5, 1816.2, (239, 128, 231)),   # split from merged blob (pink, top)
(2613.1, 1948.4, (108, 225, 242)),   # split from merged blob (cyan, bottom)
(2634.1, 2092.9, (16, 87, 57)),
(3637.5, 2246.0, (202, 4, 177)),
(3661.5, 2785.0, (21, 164, 134)),
(563.1, 2964.5, (170, 167, 14)),
(1135.9, 2988.4, (231, 97, 160)),
]

print("n =", len(blobs))

def hue_of(rgb):
    r,g,b = [c/255 for c in rgb]
    h,s,v = colorsys.rgb_to_hsv(r,g,b)
    return h*360

# sort reading orders to test
by_y = sorted(blobs, key=lambda b: b[1])
by_x = sorted(blobs, key=lambda b: b[0])

print("\n--- sorted by Y (top to bottom), hue -> letter (26 buckets) ---")
for b in by_y:
    h = hue_of(b[2])
    letter = chr(ord('A') + int(h/360*26)%26)
    print(f"y={b[1]:7.1f} x={b[0]:7.1f} rgb={b[2]} hue={h:6.1f} letter={letter}")

print("\n--- sorted by X (left to right), hue -> letter ---")
for b in by_x:
    h = hue_of(b[2])
    letter = chr(ord('A') + int(h/360*26)%26)
    print(f"x={b[0]:7.1f} y={b[1]:7.1f} rgb={b[2]} hue={h:6.1f} letter={letter}")

print("\n--- concat strings ---")
s_y = "".join(chr(ord('A') + int(hue_of(b[2])/360*26)%26) for b in by_y)
s_x = "".join(chr(ord('A') + int(hue_of(b[2])/360*26)%26) for b in by_x)
print("by_y:", s_y)
print("by_x:", s_x)
