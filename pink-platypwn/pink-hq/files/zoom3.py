from PIL import Image
import numpy as np, os
OUT = r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
im=Image.open(os.path.join(OUT,'dds_007.png')).convert('RGB')
W,H=im.size
print('card size',W,H)
# right watermark region
r=im.crop((int(W*0.6),int(H*0.35),W,H)).resize((int(W*0.4)*10,int(H*0.65)*10),Image.NEAREST)
r.save(os.path.join(OUT,'card_right_z.png'))
# bottom scrawl
b=im.crop((0,int(H*0.75),int(W*0.6),H)).resize((int(W*0.6)*10,int(H*0.25)*10),Image.NEAREST)
b.save(os.path.join(OUT,'card_bottom_z.png'))
# enhance right watermark: boost saturation/contrast of red+green faint marks
a=np.array(im.crop((int(W*0.6),int(H*0.35),W,H))).astype(int)
rr,gg,bb=a[:,:,0],a[:,:,1],a[:,:,2]
# red glyph: r notably > g,b ; green: g> r,b ; grey '5:' : dark-ish
red=(rr-np.maximum(gg,bb))>12
grn=(gg-np.maximum(rr,bb))>12
dark=(rr<180)&(gg<180)&(bb<180)
mark=red|grn|dark
out=np.where(mark,0,255).astype('uint8')
Image.fromarray(out).resize((out.shape[1]*12,out.shape[0]*12),Image.NEAREST).save(os.path.join(OUT,'card_right_bw.png'))
print('done')
