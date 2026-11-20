from PIL import Image
import os
OUT = r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
def z(name, box=None, scale=6, tag=None):
    im=Image.open(os.path.join(OUT,name)).convert('RGB')
    if box: im=im.crop(box)
    big=im.resize((im.width*scale, im.height*scale), Image.NEAREST)
    out=(tag or name.replace('.png',''))+'_z.png'
    big.save(os.path.join(OUT,out)); print(out, big.size)
z('dds_007.png', scale=6)                 # full ID card
z('png_046.png', scale=6)                 # peach carton
z('dds_005.png', scale=12)                # vent sticker full
# dds_006 sticker region
z('dds_006.png', box=(220,305,285,358), scale=16, tag='dds_006_sticker')
