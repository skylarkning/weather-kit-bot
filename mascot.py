"""Weather-aware Firefox companion placed in the hero area's left margin."""
from functools import lru_cache
from pathlib import Path
import math
from PIL import Image

ASSETS=Path(__file__).parent/'assets'/'fox'

def mood_for(forecast):
    kind=forecast.get('kind','clear')
    feels=forecast.get('feels_like',forecast.get('temperature',18))
    if kind=='storm': return 'storm'
    if feels<=0 or kind=='snow': return 'cold'
    if feels>=30: return 'hot'
    if kind=='rain': return 'rain'
    if kind in ('cloudy','fog'): return 'calm'
    return 'happy'

@lru_cache(maxsize=6)
def sprite(mood):
    path=ASSETS/f'{mood}.png'
    with Image.open(path) as im:
        image=im.convert('RGBA')
    # Keep the character within the empty left-hand area below the main weather icon.
    image.thumbnail((185,205),Image.Resampling.LANCZOS)
    return image

def draw_mascot(base,forecast,frame,count):
    mood=mood_for(forecast); image=sprite(mood)
    phase=frame/count*math.tau
    dx=round(math.sin(phase*4)) if mood=='cold' else 0
    dy=round(math.sin(phase)*1.5) if mood in ('happy','calm','hot') else 0
    position=(int(139-image.width/2)+dx,778-image.height+dy)
    base.alpha_composite(image,position)
    mask=Image.new('L',base.size)
    mask.paste(image.getchannel('A').point(lambda a:255 if a>16 else 0),position)
    return mask
