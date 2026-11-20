from PIL import Image
import numpy as np, os
OUT=r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
im=Image.open(os.path.join(OUT,'dds_005.png')).convert('RGB')
a=np.array(im).astype(int)
# pure white sticker >=235 all channels
w=(a[:,:,0]>=232)&(a[:,:,1]>=232)&(a[:,:,2]>=232)
# find the biggest connected white rectangle via column/row sums
ys,xs=np.where(w)
# restrict to the sticker: it's a solid block; find rows/cols with many white px
rowsum=w.sum(1); colsum=w.sum(0)
rr=np.where(rowsum>8)[0]; cc=np.where(colsum>8)[0]
print('rows',rr.min(),rr.max(),'cols',cc.min(),cc.max())
box=(cc.min(),rr.min(),cc.max()+1,rr.max()+1)
c=im.crop(box)
c.resize((c.width*16,c.height*16),Image.NEAREST).save(os.path.join(OUT,'s5o.png'))
c.transpose(Image.ROTATE_180).resize((c.width*16,c.height*16),Image.NEAREST).save(os.path.join(OUT,'s5r.png'))
c.transpose(Image.FLIP_LEFT_RIGHT).resize((c.width*16,c.height*16),Image.NEAREST).save(os.path.join(OUT,'s5h.png'))
print('box',box,c.size)
