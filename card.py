"""Premium animated Toronto weather card for Discord."""
import math
from datetime import date
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from atmosphere import animate, weather_symbol
from mascot import draw_mascot, mood_for, sprite
from gif_palette import make_palette, quantize_frame
from weather_icons import draw_weather_art

W, H = 900, 1600
ASSET = Path(__file__).parent / "assets" / "toronto-morning.png"

def font(size, bold=False):
    choices = ["/System/Library/Fonts/HelveticaNeue.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for path in choices:
        try: return ImageFont.truetype(path, size, index=1 if bold and path.endswith(".ttc") else 0)
        except OSError: continue
    return ImageFont.load_default()

def panel(base, box, alpha=128, radius=32):
    mask=Image.new('L',base.size); ImageDraw.Draw(mask).rounded_rectangle(box,radius,fill=255)
    base.paste(base.filter(ImageFilter.GaussianBlur(22)),(0,0),mask)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius, fill=(15, 42, 65, alpha), outline=(255, 255, 255, 105), width=2)
    base.alpha_composite(layer)

def icon(d, x, y, code, size=28):
    if code <= 1:
        d.ellipse((x-size//2,y-size//2,x+size//2,y+size//2), fill="#FFD449")
        for a in range(0, 360, 45):
            dx,dy=math.cos(math.radians(a))*size*.85,math.sin(math.radians(a))*size*.85
            d.line((x+dx*.6,y+dy*.6,x+dx,y+dy),fill="#FFE88C",width=3)
    else:
        d.ellipse((x-size*.7,y-size*.5,x+size*.2,y+size*.4),fill="#DFEEFA")
        d.ellipse((x-size*.1,y-size*.75,x+size*.8,y+size*.35),fill="#F2F8FF")
        d.rounded_rectangle((x-size,y,x+size,y+size*.5),12,fill="#E7F3FC")
        if code in (51,53,55,56,57,61,63,65,66,67,80,81,82,95,96,99):
            for dx in (-10,0,10): d.line((x+dx,y+size*.7,x+dx-5,y+size*1.1),fill="#72CFFF",width=3)
        if code in (71,73,75,77,85,86,96,99):
            for dx in (-10,0,10): d.text((x+dx,y+size*.55),"•",font=font(22,True),fill="white",anchor="ma")
        if code >= 95: d.text((x,y+size*.3),"ϟ",font=font(38,True),fill="#FFE54F",anchor="ma")

def metric_icon(d, x, y, kind):
    """Crisp, font-independent outline icons for the metric cards."""
    ink=(225,244,255,235)
    if kind == "feels":
        # Render one continuous glass outline at 4x for smooth curves and joins.
        scale=4
        mask=Image.new("L",(64*scale,72*scale),0); md=ImageDraw.Draw(mask)
        outline=[(26,43),(26,15)]
        outline += [(32+6*math.cos(math.radians(a)),15+6*math.sin(math.radians(a))) for a in range(180,361,4)]
        outline.append((38,43))
        outline += [(32+10*math.cos(math.radians(a)),51+10*math.sin(math.radians(a))) for a in range(-53,234,3)]
        outline.append((26,43))
        md.line([(px*scale,py*scale) for px,py in outline],fill=255,width=9,joint="curve")
        md.line((32*scale,25*scale,32*scale,51*scale),fill=255,width=8)
        md.ellipse((28*scale,47*scale,36*scale,55*scale),fill=255)
        for tick in (22,30,38): md.line((43*scale,tick*scale,47*scale,tick*scale),fill=255,width=6)
        d.bitmap((x-32,y-36),mask.resize((64,72),Image.Resampling.LANCZOS),fill=ink)
    elif kind == "humidity":
        # Two cubic Bezier curves form a closed, symmetric teardrop.
        points=[]
        curves=[((0,-23),(6,-11),(27,21),(0,21)),
                ((0,21),(-27,21),(-6,-11),(0,-23))]
        for p0,p1,p2,p3 in curves:
            for step in range(41):
                t=step/40; u=1-t
                px=u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0]
                py=u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]
                points.append((x+px,y+py))
        d.line(points,fill=ink,width=3,joint="curve")
        d.arc((x-8,y+2,x+6,y+14),85,160,fill=ink,width=2)
    elif kind == "wind":
        for dy,width in [(-13,32),(0,44),(13,28)]:
            d.line((x-width//2,y+dy,x+width//2,y+dy),fill=ink,width=3)
            d.arc((x+width//2-12,y+dy-8,x+width//2+4,y+dy+8),270,90,fill=ink,width=3)
    elif kind == "uv":
        d.ellipse((x-10,y-10,x+10,y+10),outline=ink,width=3)
        for a in range(0,360,45):
            dx,dy=math.cos(math.radians(a))*20,math.sin(math.radians(a))*20
            d.line((x+dx*.7,y+dy*.7,x+dx,y+dy),fill=ink,width=3)
    elif kind in ("sunrise", "sunset"):
        d.line((x-25,y+15,x+25,y+15),fill=ink,width=3); d.arc((x-15,y-8,x+15,y+22),180,360,fill=ink,width=3)
        if kind == "sunrise":
            for dx in (-19,0,19): d.line((x+dx,y-19,x+dx,y-10),fill=ink,width=3)
            d.line((x,y+3,x,y-22),fill=ink,width=2); d.line((x,y-22,x-5,y-16),fill=ink,width=2); d.line((x,y-22,x+5,y-16),fill=ink,width=2)
        else:
            for dx in (-19,0,19): d.line((x+dx,y+24,x+dx,y+32),fill=ink,width=3)
            d.line((x,y-17,x,y+5),fill=ink,width=2); d.line((x,y+5,x-5,y-1),fill=ink,width=2); d.line((x,y+5,x+5,y-1),fill=ink,width=2)
    elif kind == "eye":
        d.arc((x-27,y-16,x+27,y+16),180,360,fill=ink,width=3); d.arc((x-27,y-16,x+27,y+16),0,180,fill=ink,width=3)
        d.ellipse((x-6,y-6,x+6,y+6),outline=ink,width=3)

def make_weather_gif(forecast):
    kind=forecast.get('kind','clear')
    background=ASSET.parent / f'toronto-{kind}-v2.png'
    photo = Image.open(background if background.exists() else ASSET).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
    hours = forecast.get("hourly") or [{"time":f"{h}:00","temp":forecast["temperature"],"code":0} for h in range(7,19)]
    label = date.fromisoformat(forecast.get("date",str(date.today()))).strftime("%A, %B %-d")
    frames=[]
    for frame in range(16):
        base=photo.convert('RGBA')
        animate(base,kind,forecast.get('code',0),frame,16)
        veil=Image.new('RGBA',(W,H)); vd=ImageDraw.Draw(veil)
        for row in range(720):
            vd.line((0,row,W,row),fill=(14,27,42,int(65*(1-row/720))))
        base.alpha_composite(veil)
        d=ImageDraw.Draw(base)
        d.text((55,105),"●  Toronto",font=font(72,True),fill="white")
        d.text((112,198),label,font=font(37),fill="#D9EEFF")
        draw_weather_art(base,142,390,forecast.get('code',0),190,frame,16)
        temperature=str(forecast['temperature'])
        temperature_font=font(196,True)
        d.text((245,330),temperature,font=temperature_font,fill="white",anchor="lt")
        unit_x=245+d.textlength(temperature,font=temperature_font)+8
        d.text((unit_x,342),"°C",font=font(76),fill="#E8F5FF",anchor="lt")
        description_size=55
        while d.textlength(forecast['description'],font=font(description_size,True))>610:
            description_size-=1
        d.text((250,493),forecast["description"],font=font(description_size,True),fill="white")
        d.text((252,558),f"H {forecast['high']}°   L {forecast['low']}°",font=font(38),fill="#E0F3FF")
        mascot_mask=draw_mascot(base,forecast,frame,16)
        panel(base,(28,790,872,1125),145,36); d=ImageDraw.Draw(base)
        d.text((58,827),"Hourly Forecast",font=font(39,True),fill="white")
        d.text((660,832),"7am – 6pm",font=font(25),fill="#D6E9F6"); d.line((55,891,845,891),fill=(255,255,255,90),width=1)
        step=785/min(len(hours),12)
        for n,hour in enumerate(hours[:12]):
            x=70+n*step
            # Keep dividers out of the weather glyphs: two quiet segments read as a grid
            # without visually cutting through the clouds, rain, or snow.
            if n:
                # Each divider is exactly halfway between two hourly columns.
                divider=x-step/2
                d.line((divider,908,divider,1090),fill=(255,255,255,62),width=1)
            d.text((x,918),hour["time"].lstrip("0"),font=font(19,True),fill="#E8F6FF",anchor="ma"); draw_weather_art(base,x,982,hour['code'],48,frame,16)
            d.text((x,1050),f"{hour['temp']}°",font=font(25,True),fill="white",anchor="ma")
        cards = [
            (30,232,"Feels Like",f"{forecast['feels_like']}°","feels"),
            (244,446,"Humidity",f"{forecast['humidity']}%","humidity"),
            (458,660,"Wind",f"{forecast['wind']} km/h","wind"),
            (672,870,"UV Index",f"{forecast.get('uv_index', 0)}","uv"),
        ]
        for x1,x2,label2,value,kind2 in cards:
            panel(base,(x1,1155,x2,1355),125,30); d=ImageDraw.Draw(base)
            metric_icon(d,x1+45,1200,kind2)
            d.text((x1+24,1245),label2,font=font(23),fill="#D9EDFA"); d.text((x1+24,1282),value,font=font(40,True),fill="white")
        # The bottom row follows the native reference: one shared sun-times card and one visibility card.
        panel(base,(30,1380,560,1518),125,30); panel(base,(575,1380,870,1518),125,30); d=ImageDraw.Draw(base)
        metric_icon(d,76,1440,"sunrise"); d.text((122,1410),"Sunrise",font=font(23),fill="#D9EDFA"); d.text((122,1452),forecast["sunrise"],font=font(35,True),fill="white")
        d.line((286,1400,286,1498),fill=(255,255,255,70),width=1)
        metric_icon(d,334,1440,"sunset"); d.text((380,1410),"Sunset",font=font(23),fill="#D9EDFA"); d.text((380,1452),forecast["sunset"],font=font(35,True),fill="white")
        metric_icon(d,625,1440,"eye"); d.text((670,1410),"Visibility",font=font(23),fill="#D9EDFA"); d.text((670,1452),f"{forecast.get('visibility', 10)} km",font=font(35,True),fill="white")
        if not frames:
            palette=make_palette(base,sprite(mood_for(forecast)))
        frames.append(quantize_frame(base,palette,mascot_mask))
    out=BytesIO(); frames[0].save(out,format="GIF",save_all=True,append_images=frames[1:],duration=110,loop=0,optimize=True,disposal=1)
    return out.getvalue()
