from PIL import Image
import numpy as np, os

OUT = r'c:\Users\mayan\OneDrive\Desktop\ctf\pink_hq\view'

def process(fname, tag):
    im = Image.open(os.path.join(OUT, fname)).convert('RGB')
    a = np.array(im).astype(int)
    r,g,b = a[:,:,0],a[:,:,1],a[:,:,2]
    # white sticker = all channels high
    white = (r>200)&(g>200)&(b>200)
    # find sticker bbox (largest near-white cluster) -> just use all white pixels bbox
    ys,xs = np.where(white)
    if len(xs)==0:
        print(fname,'no white'); return
    x0,x1,y0,y1 = xs.min(),xs.max(),ys.min(),ys.max()
    crop = im.crop((x0,y0,x1+1,y1+1))
    ca = np.array(crop).astype(int)
    rr,gg,bb = ca[:,:,0],ca[:,:,1],ca[:,:,2]
    # text = darker than sticker white
    dark = (rr<160)|(gg<160)|(bb<160)
    bw = Image.fromarray((np.where(dark,0,255)).astype('uint8'))
    scale = max(1, 1200//max(bw.size))
    for name,img in [('orig',bw),('fliph',bw.transpose(Image.FLIP_LEFT_RIGHT)),
                     ('flipv',bw.transpose(Image.FLIP_TOP_BOTTOM)),
                     ('rot180',bw.transpose(Image.ROTATE_180))]:
        big = img.resize((img.width*scale, img.height*scale), Image.NEAREST)
        big.save(os.path.join(OUT, f'{tag}_{name}.png'))
    print(fname,'sticker bbox',(x0,y0,x1,y1),'crop',bw.size,'scale',scale)

process('dds_005.png','L5')
process('dds_006.png','L6')
