"""Detailed weather artwork selected from Open-Meteo WMO codes."""
from functools import lru_cache
from pathlib import Path
import math
from PIL import Image

ASSETS=Path(__file__).parent/'assets'/'weather-icons'

def icon_for(code):
    if code in (0,1):return 'sunny'
    if code==2:return 'partly-cloudy'
    if code==3:return 'cloudy'
    if code in (45,48):return 'fog'
    if code in (56,57,66,67):return 'freezing-rain'
    if code in (71,73,75,77,85,86):return 'snow'
    if code==95:return 'storm'
    if code in (96,99):return 'hail'
    return 'rain'

@lru_cache(maxsize=32)
def artwork(name,size):
    with Image.open(ASSETS/f'{name}.png') as source:
        image=source.convert('RGBA')
    image.thumbnail((size,size),Image.Resampling.LANCZOS)
    return image

def draw_weather_art(base,x,y,code,size,frame=0,count=16):
    name=icon_for(code); image=artwork(name,size)
    bob=round(math.sin(frame/count*math.tau)*2) if size>100 else 0
    base.alpha_composite(image,(int(x-image.width/2),int(y-image.height/2)+bob))
