from PIL import Image
import os
OUT=r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
names=['png_043','png_044','png_045','png_046','png_048','png_049','png_050','png_051','png_052','png_053','png_054']
# montage of 4x upscales
ims=[Image.open(os.path.join(OUT,n+'.png')).convert('RGB') for n in names]
cell_w=max(i.width for i in ims)*3
cell_h=max(i.height for i in ims)*3
cols=3; rows=(len(ims)+cols-1)//cols
from PIL import ImageDraw
sheet=Image.new('RGB',(cols*cell_w, rows*(cell_h+24)),(30,30,30))
d=ImageDraw.Draw(sheet)
for i,(n,im) in enumerate(zip(names,ims)):
    big=im.resize((im.width*3,im.height*3),Image.LANCZOS)
    cx=(i%cols)*cell_w; cy=(i//cols)*(cell_h+24)
    d.text((cx+2,cy+2),n,fill=(255,255,0))
    sheet.paste(big,(cx+2,cy+24))
sheet.save(os.path.join(OUT,'_drinks.png'))
print('saved',sheet.size)
