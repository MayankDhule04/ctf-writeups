from PIL import Image
import numpy as np, os
OUT=r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
im=Image.open(os.path.join(OUT,'dds_007.png')).convert('RGB')
a=np.array(im).astype(int)
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
red=((r-g)>18)&((r-b)>18)
grey=(abs(r-g)<22)&(abs(g-b)<22)&(r<170)&(r>60)
out=np.full(a.shape[:2],255,np.uint8)
out[grey]=120
out[red]=0
big=Image.fromarray(out).resize((im.width*8,im.height*8),Image.NEAREST)
big.save(os.path.join(OUT,'card_redgrey.png'))
print('saved', big.size)
