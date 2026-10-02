"""Render example cards for every mascot mood, including temperature extremes."""
from pathlib import Path
from PIL import Image, ImageDraw
from card import make_weather_gif, font
from mascot import mood_for

out=Path(__file__).resolve().parent.parent/'outputs'/'mascot-weather'
out.mkdir(parents=True,exist_ok=True)
examples=[('happy','clear',0,'Sunny',22,23),('calm','cloudy',3,'Overcast',16,15),
          ('rain','rain',63,'Rain',12,10),('cold','snow',75,'Heavy snow',-12,-19),
          ('hot','clear',0,'Sunny',33,38),('storm','storm',95,'Thunderstorm',21,20)]
sheet=Image.new('RGB',(1200,1480),'#14263c')
for n,(mood,kind,code,description,temp,feels) in enumerate(examples):
    sample={'date':'2026-10-02','description':description,'kind':kind,'code':code,
            'temperature':temp,'high':temp+3,'low':temp-4,'feels_like':feels,
            'humidity':72,'wind':22,'uv_index':4,'visibility':10,'sunrise':'07:22','sunset':'18:58',
            'hourly':[{'time':f'{h:02}:00','temp':temp+min(h-7,3),'code':code} for h in range(7,19)]}
    assert mood_for(sample)==mood
    path=out/f'{mood}.gif';path.write_bytes(make_weather_gif(sample))
    with Image.open(path) as im:tile=im.convert('RGB').resize((390,693),Image.Resampling.LANCZOS)
    x=(n%3)*400;y=(n//3)*740;sheet.paste(tile,(x,y))
    ImageDraw.Draw(sheet).text((x+10,y+702),f'{mood.title()} · feels {feels}°C',font=font(20),fill='white')
sheet.save(out.parent/'mascot-weather-comparison.jpg',quality=95)
print('Rendered six weather-aware mascot cards')
