from PIL import Image
import numpy as np, os, base64
OUT = r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
print('base64 ODogX2lz ->', base64.b64decode('ODogX2lz').decode())
# dds_006 sticker
im=Image.open(os.path.join(OUT,'dds_006.png')).convert('RGB').crop((220,305,285,358))
im.transpose(Image.ROTATE_180).resize((65*14,53*14),Image.NEAREST).save(os.path.join(OUT,'s6_rot.png'))
# dds_005 sticker: find white box on left
im5=Image.open(os.path.join(OUT,'dds_005.png')).convert('RGB')
a=np.array(im5).astype(int)
white=(a[:,:,0]>190)&(a[:,:,1]>190)&(a[:,:,2]>190)
ys,xs=np.where(white)
print('dds005 white bbox', xs.min(),ys.min(),xs.max(),ys.max())
c=im5.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
c.transpose(Image.ROTATE_180).resize((c.width*14,c.height*14),Image.NEAREST).save(os.path.join(OUT,'s5_rot.png'))
c.resize((c.width*14,c.height*14),Image.NEAREST).save(os.path.join(OUT,'s5_orig.png'))
print('done', c.size)
