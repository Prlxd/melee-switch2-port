# The picker's two panels (640x720 each), drawn from scratch: art/left.png and art/right.png.
# Usage: python3 art.py   (make.py then lays the picker over them)
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import os
W,H=640,720; G=os.environ.get('POPPINS_DIR','/usr/share/fonts/truetype/google-fonts')+'/'
HERE=os.path.dirname(os.path.abspath(__file__))
def F(n,s): return ImageFont.truetype(G+'Poppins-%s.ttf'%n,s)
rng=np.random.default_rng(7)
def noise(scale,seed):
    r=np.random.default_rng(seed); acc=np.zeros((H,W))
    for i,s in enumerate([scale,scale/2,scale/4,scale/8]):
        n=r.random((int(H/s)+2,int(W/s)+2))
        im=Image.fromarray((n*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)
        acc+=np.asarray(im,float)/255*(0.5**i)
    acc-=acc.min(); return acc/acc.max()
def lerp(a,b,t): return a+(b-a)*t
def grad(stops):
    ys=np.linspace(0,1,H); out=np.zeros((H,3))
    for i in range(len(stops)-1):
        (p0,c0),(p1,c1)=stops[i],stops[i+1]
        m=(ys>=p0)&(ys<=p1); t=((ys[m]-p0)/(p1-p0))[:,None]
        out[m]=np.array(c0)*(1-t)+np.array(c1)*t
    return np.repeat(out[:,None,:],W,axis=1)
def left():
    ys=np.arange(H)[:,None]; xs=np.arange(W)[None,:]
    t=np.clip((xs/W)*0.45+(1-ys/H)*0.55,0,1)[...,None]           # crimson bottom-left, indigo top-right
    base=np.array([120,22,40])*(1-t)+np.array([38,22,86])*t
    sm=noise(220,41); sm2=noise(90,42)
    base=base*(0.82+0.36*sm[...,None])+((sm2-0.5)*12)[...,None]
    vig=np.clip(1-(((xs-W/2)/(W*0.75))**2+((ys-H*0.42)/(H*0.7))**2),0,1)
    base=base*(0.6+0.4*vig[...,None])
    im=Image.fromarray(np.clip(base,0,255).astype(np.uint8)); cy=262
    f1=F('Light',34); f2=F('Medium',112); f3=F('Medium',22)
    GOLD=(255,214,150)
    glow=Image.new('L',(W,H),0); ImageDraw.Draw(glow).text((W/2,cy+4),'MELEE',font=f2,fill=255,anchor='mm')
    im=Image.composite(Image.new('RGB',(W,H),(255,150,90)),im,glow.filter(ImageFilter.GaussianBlur(18)).point(lambda v:int(v*0.55)))
    d=ImageDraw.Draw(im)
    d.text((W/2,cy-78),'SUPER SMASH BROS.',font=f1,fill=GOLD,anchor='mm')
    d.text((W/2,cy+4),'MELEE',font=f2,fill=(255,250,244),anchor='mm')
    tag='NTSC  1.02'; tw=d.textlength(tag,font=f3)
    d.rounded_rectangle([W/2-tw/2-18,cy+92,W/2+tw/2+18,cy+128],radius=18,outline=GOLD,width=2)
    d.text((W/2,cy+110),tag,font=f3,fill=GOLD,anchor='mm')
    return im
def smoke(seed):
    base=np.full((H,W,3),51.0)
    sm=noise(220,seed); sm2=noise(90,seed+1)
    base+= ((sm-0.5)*26+(sm2-0.5)*10)[...,None]
    ys=np.arange(H)[:,None]; xs=np.arange(W)[None,:]
    vig=np.clip(1-(((xs-W/2)/(W*0.75))**2+((ys-H*0.42)/(H*0.7))**2),0,1)
    base=base*(0.72+0.28*vig[...,None])
    return Image.fromarray(np.clip(base,0,255).astype(np.uint8))
CY=(125,228,247)
def right():
    im=smoke(21); d=ImageDraw.Draw(im); cy=270
    f=F('Medium',128); hr=58; gap=16
    two=d.textbbox((0,0),'2',font=f,anchor='lm'); xx=d.textbbox((0,0),'XX',font=f,anchor='lm')
    w2=two[2]-two[0]; wx=xx[2]-xx[0]; total=w2+gap+2*hr*0.866*2/2*2/2*2+gap+wx
    hexw=2*hr*0.866
    total=w2+gap+hexw+gap+wx; x0=(W-total)/2
    hx=x0+w2+gap+hexw/2; xxx=hx+hexw/2+gap
    beam=Image.new('L',(W,H),0); bd=ImageDraw.Draw(beam)
    bd.polygon([(hx,cy-hr),(hx,cy+hr),(xxx+wx+30,cy+hr*0.62),(xxx+wx+30,cy-hr*0.62)],fill=170)
    beam=beam.filter(ImageFilter.GaussianBlur(8))
    grad_x=Image.fromarray(np.tile(np.clip(1-(np.arange(W)-hx)/(wx+gap+90.0),0,1)[None,:]*255,(H,1)).astype(np.uint8))
    beam=ImageChops.multiply(beam,grad_x)
    d.text((xxx-xx[0],cy),'XX',font=f,fill=(38,38,38),anchor='lm',stroke_width=2,stroke_fill=(150,225,240))
    im=Image.composite(Image.new('RGB',(W,H),CY),im,beam.point(lambda v:int(v*0.5)))
    d=ImageDraw.Draw(im)
    d.text((x0-two[0],cy),'2',font=f,fill=CY,anchor='lm')
    pts=lambda r:[(hx+r*math.cos(math.radians(90+60*i)),cy+r*math.sin(math.radians(90+60*i))) for i in range(6)]
    d.polygon(pts(hr),fill=CY); d.polygon(pts(hr*0.52),fill=(51,51,51))
    f2=F('Light',34)
    for i,t in enumerate(['TOURNAMENT','EDITION']):
        d.text((W/2,cy+112+i*44),t,font=f2,fill=(235,235,235),anchor='mm')
    return im
# a light blur, so the panels read soft like painted art rather than sharp vector type
SOFT=ImageFilter.GaussianBlur(0.7)
left().filter(SOFT).save(os.path.join(HERE,'art','left.png')); right().filter(SOFT).save(os.path.join(HERE,'art','right.png'))
