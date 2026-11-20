from PIL import Image
from PIL.ExifTags import TAGS

p = r"C:\Users\mayan\OneDrive\Desktop\ctf\dome ctf\IMG_4421.jpg"
im = Image.open(p)
print("size:", im.size, "mode:", im.mode, "format:", im.format)
print("info:", im.info)

exif = im.getexif()
if exif:
    for k, v in exif.items():
        tag = TAGS.get(k, k)
        print(tag, "=", v)
else:
    print("no exif")

# raw bytes scan for text / comments
with open(p, "rb") as fh:
    data = fh.read()
import re
print("\n--- printable runs > 6 chars anywhere in file ---")
for m in re.finditer(rb"[ -~]{6,}", data):
    s = m.group()
    if s not in (b"JFIF", ):
        print(m.start(), s)
