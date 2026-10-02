"""Soft atmospheric motion and antialiased weather symbols."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

def animate(base, kind, code, frame, count):
    w,h=base.size; phase=frame/count
    layer=Image.new('RGBA',base.size); d=ImageDraw.Draw(layer)
    rng=random.Random(42)
    heavy=code in (55,57,65,67,75,82,86,95,96,99)
    light=code in (51,56,61,66,71,77,80,85)
    intensity=0 if light else 2 if heavy else 1
    if kind in ('rain','storm','snow'):
        density=(35,130,380)[intensity] if kind!='snow' else (28,110,300)[intensity]
        for n in range(density):
            x=rng.randrange(w); y=rng.randrange(h); depth=rng.random()
            travel=(280,540,920)[intensity] if kind!='snow' else (95,170,310)[intensity]
            drift=(20,80,290)[intensity] if kind!='snow' else (12,55,240)[intensity]
            px=(x-phase*drift+ (math.sin(phase*math.tau+n)*12 if kind=='snow' else 0))%w
            py=(y+phase*travel*(.5+depth))%h
            alpha=int((28,45,65)[intensity]+depth*110)
            if kind=='snow':
                r=(.7,1.2,1.8)[intensity]+depth*(1.8,3,4)[intensity]
                d.ellipse((px-r,py-r,px+r,py+r),fill=(244,249,255,alpha))
                if heavy and depth>.7:
                    d.line((px,py,px-10,py+6),fill=(244,249,255,alpha//2),width=2)
            else:
                length=(5,14,26)[intensity]+depth*(8,18,30)[intensity]
                slant=(1,5,18)[intensity]
                d.line((px,py,px-slant,py+length),fill=(210,226,238,alpha),width=1 if depth<.7 else 2)
                if code in (56,57,66,67,96,99) and n%3==0:
                    d.ellipse((px-2,py-2,px+2,py+2),fill=(224,243,255,alpha))
        base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(.45)))
        if heavy:
            mist=Image.new('RGBA',base.size); md=ImageDraw.Draw(mist)
            for n in range(4):
                cy=650+n*190; md.ellipse((-150,cy-80,w+150,cy+80),fill=(205,220,235,18))
            base.alpha_composite(mist.filter(ImageFilter.GaussianBlur(65)))
    elif kind=='clear':
        # Slow breathing sunlight and independent reflected glints on Lake Ontario.
        glow=Image.new('RGBA',base.size); gd=ImageDraw.Draw(glow)
        strength=int(13+9*math.sin(phase*math.tau))
        gd.ellipse((w-370,-170,w+210,470),fill=(255,237,179,strength))
        base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
        for n in range(55):
            px=rng.randrange(int(w*.48),w); py=rng.randrange(int(h*.59),int(h*.79))
            shimmer=max(0,math.sin(phase*math.tau*2+n*1.73))**6
            alpha=int(170*shimmer)
            span=2+rng.randrange(10)
            d.line((px-span,py,px+span,py),fill=(255,245,211,alpha),width=1)
        base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(.6)))
    elif kind in ('fog','cloudy'):
        for n in range(6):
            cx=(n*220+math.sin(phase*math.tau)*35)%w; cy=200+n*110
            d.ellipse((cx-350,cy-95,cx+350,cy+95),fill=(225,235,240,13 if kind=='cloudy' else 28))
        base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(65)))
    if kind=='storm' and frame==6:
        base.alpha_composite(Image.new('RGBA',base.size,(220,229,255,30)))

def weather_symbol(draw,x,y,code,size):
    scale=3; side=int(size*3.3); center=side/2
    im=Image.new('RGBA',(side*scale,side*scale)); d=ImageDraw.Draw(im)
    def ellipse(box,fill):d.ellipse(tuple(int(v*scale) for v in box),fill=fill)
    def line(points,fill,width=1):d.line([(int(a*scale),int(b*scale)) for a,b in points],fill=fill,width=max(1,int(width*scale)))
    c=center; s=size
    if code in (0,1,2):
        sunx=c if code<2 else c-s*.35; suny=c if code<2 else c-s*.25
        for a in range(0,360,45):
            rad=math.radians(a); line([(sunx+math.cos(rad)*s*.62,suny+math.sin(rad)*s*.62),(sunx+math.cos(rad)*s*.8,suny+math.sin(rad)*s*.8)],(255,222,129,230),s*.025)
        for r in range(int(s*.47),0,-1):
            t=r/(s*.47); ellipse((sunx-r,suny-r,sunx+r,suny+r),(255,int(223-35*t),int(137-74*t),255))
    if code not in (0,1):
        cloud=Image.new('L',im.size); cd=ImageDraw.Draw(cloud)
        for dx,dy,r in [(-.43,.08,.30),(-.12,-.13,.40),(.32,.02,.32)]:
            cd.ellipse(tuple(int(v*scale) for v in (c+(dx-r)*s,c+(dy-r)*s,c+(dx+r)*s,c+(dy+r)*s)),fill=255)
        cd.rounded_rectangle(tuple(int(v*scale) for v in (c-.7*s,c,c+.66*s,c+.35*s)),radius=int(s*.15*scale),fill=255)
        shade=Image.new('RGBA',im.size); sd=ImageDraw.Draw(shade)
        dark=code>=95
        for row in range(im.height):
            t=row/im.height; val=int((203 if dark else 255)-t*(70 if dark else 40)); sd.line((0,row,im.width,row),fill=(val,min(255,val+7),min(255,val+14),255))
        im.paste(shade,(0,0),cloud)
        if code in (45,48):
            for dy in (.48,.65):line([(c-.65*s,c+dy*s),(c+.65*s,c+dy*s)],(226,235,244,190),s*.04)
        elif code in (71,73,75,77,85,86):
            for dx in (-.4,0,.4):
                sx=c+dx*s; sy=c+s*.65
                for a in (0,60,120):
                    rad=math.radians(a); line([(sx-math.cos(rad)*s*.12,sy-math.sin(rad)*s*.12),(sx+math.cos(rad)*s*.12,sy+math.sin(rad)*s*.12)],(240,248,255,255),s*.035)
        elif code>=51:
            for dx in (-.4,0,.4):line([(c+dx*s,c+s*.46),(c+(dx-.1)*s,c+s*.73)],(139,205,245,240),s*.035)
        if code>=95:
            d.polygon([(int((c+dx*s)*scale),int((c+dy*s)*scale)) for dx,dy in [(.1,.2),(-.15,.55),(.04,.53),(-.08,.85),(.3,.4),(.1,.42)]],fill=(255,220,95,255))
    im=im.resize((side,side),Image.Resampling.LANCZOS)
    # Composite the shaded symbol onto the drawing's backing image.
    draw._image.alpha_composite(im,(int(x-center),int(y-center)))
