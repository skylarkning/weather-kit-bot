"""Generate every supported weather-code preview and a comparison sheet."""
from pathlib import Path
from PIL import Image, ImageDraw
from card import make_weather_gif, font
from weather import WEATHER_CODES

out=Path(__file__).resolve().parent.parent / 'outputs' / 'weather-scenarios'
out.mkdir(parents=True,exist_ok=True)
sheet=Image.new('RGB',(1200, ((len(WEATHER_CODES)+3)//4)*585),'#12263c')
for n,(code,(description,kind)) in enumerate(WEATHER_CODES.items()):
    temp=-5 if kind=='snow' else 1 if code in (48,56,57,66,67) else 18
    sample={'date':'2026-10-02','description':description,'kind':kind,'code':code,'temperature':temp,'high':temp+4,'low':temp-4,'feels_like':temp-2,'humidity':78,'wind':16,'uv_index':2,'visibility':2 if kind=='fog' else 10,'sunrise':'07:22','sunset':'18:58','hourly':[{'time':f'{h:02}:00','temp':temp+min(h-7,4),'code':code} for h in range(7,19)]}
    path=out / f'{code:02}-{description.lower().replace(" ","-")}.gif'
    path.write_bytes(make_weather_gif(sample))
    with Image.open(path) as im:
        tile=im.convert('RGB').resize((290,516),Image.Resampling.LANCZOS)
    x=(n%4)*300; y=(n//4)*585
    sheet.paste(tile,(x,y)); ImageDraw.Draw(sheet).text((x+5,y+526),f'{code}: {description}',font=font(15),fill='white')
sheet.save(out.parent/'all-weather-scenarios.jpg',quality=90)
print(f'Generated {len(WEATHER_CODES)} animated previews')
