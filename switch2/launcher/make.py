# Launcher screens and the NRO icon. Everything is drawn 3x too big and scaled down, so every
# edge (circles, rounded corners, hexagons) comes out smooth. Screens are packed (zlib, RGBA
# 1280x720) into launcher_art.h.
import zlib, sys, math, os
# Usage: python3 make.py <version> <melee-unlocked checkout>
# Writes <checkout>/port/switch2/launcher_art.h, plus icon.jpg and preview PNGs next to this script.
HERE=os.path.dirname(os.path.abspath(__file__)); MU=sys.argv[2] if len(sys.argv)>2 else '.'
os.makedirs(os.path.join(HERE,'preview'),exist_ok=True)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K=3; W,H=1280,720
G=os.environ.get('POPPINS_DIR','/usr/share/fonts/truetype/google-fonts')+'/'   # Poppins (Google Fonts, OFL)
def F(n,s): return ImageFont.truetype(G+'Poppins-%s.ttf'%n,int(s*K))
BG=(51,51,51); CY=(125,228,247); WH=(255,255,255); DIM=(150,150,150); DARK=(38,38,38); SEL=(44,62,66)
VER=sys.argv[1]
def k(v): return [k(x) for x in v] if isinstance(v,(list,tuple)) else v*K
class D:   # ImageDraw in screen units
    def __init__(s,im): s.im=im; s.d=ImageDraw.Draw(im)
    def line(s,p,fill,width=1): s.d.line(k(p),fill=fill,width=int(width*K))
    def rect(s,b,fill): s.d.rectangle(k(b),fill=fill)
    def rrect(s,b,radius,fill=None,outline=None,width=1): s.d.rounded_rectangle(k(b),radius=radius*K,fill=fill,outline=outline,width=int(width*K))
    def ring(s,cx,cy,r,col,w,inside): s.d.ellipse(k([cx-r,cy-r,cx+r,cy+r]),fill=col); s.d.ellipse(k([cx-r+w,cy-r+w,cx+r-w,cy+r-w]),fill=inside)
    def hexagon(s,cx,cy,r,col,w,inside):
        P=lambda rr:[(K*(cx+rr*math.cos(math.radians(60*i+30))),K*(cy+rr*math.sin(math.radians(60*i+30)))) for i in range(6)]
        s.d.polygon(P(r+w/2),fill=col); s.d.polygon(P(r-w/2),fill=inside)
    def text(s,p,t,font,fill,anchor='la'): s.d.text(k(p),t,font=font,fill=fill,anchor=anchor)
    def tw(s,t,font): return s.d.textlength(t,font=font)/K
def new(w=W,h=H): return Image.new('RGB',(w*K,h*K),BG)
def done(im,size=None): return im.resize(size or (im.width//K,im.height//K),Image.LANCZOS)
def key(d,x,y,kk,label):
    d.d.ellipse(k([x,y,x+34,y+34]),outline=CY+(255,),width=2*K); d.text((x+17,y+17),kk,F('Medium',20),CY+(255,),'mm')
    d.text((x+46,y+17),label,F('Light',20),WH+(255,),'lm'); return x+46+d.tw(label,F('Light',20))+44
PX=[0,427,853]; PW=[427,426,427]   # three panels: Melee, 20XX TE, Slippi
NAMES=[('Super Smash Bros. Melee','The original game'),('20XX Tournament Edition','Tournament settings, 20XX CPUs'),
       ('Slippi Online','Play online with Slippi accounts')]
def overlay(choice,default):
    im=Image.new('RGBA',(W*K,H*K),(0,0,0,0)); d=D(im)
    for i in range(3):                           # the panels not chosen go dark
        if i!=choice: d.rect([PX[i],0,PX[i]+PW[i],H],(0,0,0,170))
    # a shade at the top and bottom, so the type reads on any picture
    sh=Image.new('L',(1,H*K),0)
    for y in range(H*K):
        yy=y/K; sh.putpixel((0,y),int(max(max(0,1-yy/90)*170,min(1,max(0,(yy-400)/130))*235)))
    sh=sh.resize((W*K,H*K)); c=Image.new('L',im.size,10); im.alpha_composite(Image.merge('RGBA',(c,c,c,sh)))
    d=D(im)
    for x in (427,853): d.rect([x-1,0,x+1,H],(0,0,0,140))   # thin seams between the panels
    d.rect([PX[choice],H-6,PX[choice]+PW[choice],H],CY+(255,))   # the chosen panel: a cyan bar along its bottom
    # corners: the port's name on the left, version and credit on the right
    t='MELEE'; f=F('Light',22); f2=F('Medium',22); tw=d.tw(t,f)
    d.text((26,34),t,f,WH+(255,),'lm'); d.text((26+tw+8,34),'SWITCH 2 PORT',f2,CY+(255,),'lm')
    d.text((W-26,34),'v'+VER+'  ·  Prlxd',F('Light',16),(200,200,200,255),'rm')
    vw=d.tw('v'+VER+'  ·  Prlxd',F('Light',16)); fo=F('Light',18); ow=d.tw('Options',fo)
    ox=W-26-vw-36-ow-36
    d.d.ellipse(k([ox,34-14,ox+28,34+14]),outline=CY+(255,),width=2*K); d.text((ox+14,34),'X',F('Medium',16),CY+(255,),'mm')
    d.text((ox+38,34),'Options',fo,WH+(255,),'lm')
    for i,(title,sub) in enumerate(NAMES):
        cx=PX[i]+PW[i]/2; on=choice==i
        d.text((cx,520),title,F('Medium',25),(WH if on else (150,150,150))+(255,),'mm')
        d.text((cx,552),sub,F('Light',16),((215,215,215) if on else (115,115,115))+(255,),'mm')
        if default==i+1:
            tt='DEFAULT'; ff=F('Medium',15); w=d.tw(tt,ff)
            d.rrect([cx-w/2-13,468,cx+w/2+13,494],13,fill=CY+(255,)); d.text((cx,481),tt,ff,(30,30,30,255),'mm')
    # the buttons and the hint, centred on the screen under the panels
    items=[('A','Start and set as default'),('Y','Start once')]; f=F('Light',20)
    x=W/2-(sum(46+d.tw(l,f)+44 for _,l in items)-44)/2
    for kk,l in items: x=key(d,x,606,kk,l)
    d.text((W/2,664),'Your default then starts straight away.',F('Light',15),(200,200,200,255),'mm')
    d.text((W/2,686),'To come back here, press L just after launching.',F('Light',15),CY+(255,),'mm')
    return im.resize((W,H),Image.LANCZOS)
def slippi_art():
    # Original art (no Slippi logo): a dark green field and the words in the port's font, laid out
    # like the Melee panel (title block in the middle, NTSC 1.02 badge at the same height).
    w,h=427*K,720*K; top=(22,62,42); bot=(26,30,28)
    g=Image.new('RGB',(1,h))
    for y in range(h):
        t=y/h; g.putpixel((0,y),tuple(int(top[c]+(bot[c]-top[c])*t) for c in range(3)))
    im=g.resize((w,h)); cx=213.5
    glow=Image.new('L',im.size,0); D(glow).text((cx,246),'SLIPPI',F('Medium',96),255,'mm')
    glow=glow.filter(ImageFilter.GaussianBlur(18*K))
    im.paste(Image.composite(Image.new('RGB',im.size,(70,190,120)),im,glow.point(lambda v:int(v*0.5))),(0,0)); d=D(im)
    G2=(120,215,160)
    d.text((cx,246),'SLIPPI',F('Medium',96),(235,245,238),'mm')
    d.text((cx,312),'O N L I N E',F('Medium',30),G2,'mm')
    d.rrect([cx-73,355,cx+73,389],17,outline=(120,200,150),width=2); d.text((cx,372),'NTSC 1.02',F('Medium',17),(150,215,175),'mm')
    return done(im)
def crop(img,w):   # the middle w columns of a 640x720 picture
    x=(640-w)//2; return img.crop((x,0,x+w,720))
src=[Image.open(os.path.join(HERE,'art','%s.png'%n)).convert('RGB').resize((640,720),Image.LANCZOS) for n in ('left','right')]
panels=[crop(src[0],PW[0]),crop(src[1],PW[1]),slippi_art()]
out=['// Generated by launcher/make.py. The three panel pictures are zlib-packed RGB (427, 426 and 427\n// wide, 720 high); each overlay is zlib-packed RGBA 1280x720 laid over them.\n#include <cstdint>\n#include <cstddef>\n']
total=0
def pack_bytes(name,raw):
    global total
    z=zlib.compress(raw,9); total+=len(z); out.append('static const uint8_t art_%s[] = {%s};\n'%(name,','.join(map(str,z))))
for i,pnl in enumerate(panels): pack_bytes('panel%d'%i,pnl.tobytes())
for c in (0,1,2):
    for dflt in (0,1,2,3):
        ov=overlay(c,dflt); pack_bytes('ov_%d_%d'%(c,dflt),ov.tobytes())
        full=Image.new('RGB',(W,H))
        for i,pnl in enumerate(panels): full.paste(pnl,(PX[i],0))
        full=full.convert('RGBA'); full.alpha_composite(ov)
        full.convert('RGB').save(os.path.join(HERE,'preview','picker_%d_%d.png'%(c,dflt)))
out.append('struct LauncherArt { const uint8_t* data; size_t size; };\n')
out.append('static const int art_panel_x[3] = {0, 427, 853}, art_panel_w[3] = {427, 426, 427};\n')
out.append('static const LauncherArt art_panel[3] = {%s};\n'%','.join('{art_panel%d, sizeof art_panel%d}'%(i,i) for i in range(3)))
out.append('static const LauncherArt art_overlay[3][4] = {%s};\n'%','.join('{'+','.join('{art_ov_%d_%d, sizeof art_ov_%d_%d}'%(c,d,c,d) for d in range(4))+'}' for c in (0,1,2)))
open(os.path.join(MU,'port','switch2','launcher_art.h'),'w').write(''.join(out)); print(total)
# NRO icon, same style (drawn at 1024, K=1 coordinates scaled by hand)
K=4; S=256; im=Image.new('RGB',(S*K,S*K),BG); d=D(im)
g=Image.new('L',im.size,0); D(g).hexagon(S/2,90,52,255,15,0); g=g.filter(ImageFilter.GaussianBlur(10*K))
im.paste(Image.composite(Image.new('RGB',im.size,(70,150,165)),im,g.point(lambda v:int(v*0.7))),(0,0)); d=D(im)
d.hexagon(S/2,90,52,CY,11.5,BG)
for x in range(S*K):
    a=min(1,x/(30*K),(S*K-x)/(30*K)); c=tuple(int(BG[i]+(WH[i]-BG[i])*a) for i in range(3)); d.d.line([(x,167*K),(x,169*K)],fill=c)
d.text((S/2,90),'M',F('Medium',47),WH,'mm')
d.text((S/2,192),'MELEE',F('Medium',37),WH,'mm'); d.text((S/2,226),'SWITCH 2',F('Medium',21),CY,'mm')
done(im,(256,256)).save(os.path.join(HERE,'icon.jpg'),quality=97)
