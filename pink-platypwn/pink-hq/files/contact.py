from PIL import Image
import os, glob

OUT = r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'
files = sorted([f for f in glob.glob(os.path.join(OUT,'*.png'))
                if os.path.basename(f).startswith(('dds_','png_'))
                and 'text' not in f and 'enhanced' not in f and 'red' not in f
                and 'zoom' not in f])
cell=240
cols=7
rows=(len(files)+cols-1)//cols
sheet=Image.new('RGB',(cols*cell, rows*cell*1+rows*18),(40,40,40))
from PIL import ImageDraw
d=ImageDraw.Draw(sheet)
for i,f in enumerate(files):
    im=Image.open(f).convert('RGB')
    im.thumbnail((cell-8,cell-8))
    cx=(i%cols)*cell; cy=(i//cols)*(cell+18)
    sheet.paste(im,(cx+4,cy+18))
    d.text((cx+4,cy+4), os.path.basename(f).replace('.png',''), fill=(255,255,0))
sheet.save(os.path.join(OUT,'_contact.png'))
print('files',len(files),'saved _contact.png', sheet.size)
