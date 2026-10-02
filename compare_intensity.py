"""Compare sunny motion and three precipitation intensities in one looping preview."""
from pathlib import Path
from PIL import Image, ImageDraw
from card import font

out=Path(__file__).resolve().parent.parent/'outputs'
names=['00-clear-sky','61-light-rain','63-rain','65-heavy-rain','71-light-snow','73-snow','75-heavy-snow']
labels=['Sunny','Light rain','Moderate rain','Heavy rain','Light snow','Moderate snow','Heavy snow']
sources=[Image.open(out/'weather-scenarios'/f'{name}.gif') for name in names]
frames=[]
for frame in range(16):
    sheet=Image.new('RGB',(1680,355),'#15263b'); d=ImageDraw.Draw(sheet)
    for n,source in enumerate(sources):
        source.seek(frame%source.n_frames)
        tile=source.convert('RGB').crop((0,0,900,1125)).resize((240,300),Image.Resampling.LANCZOS)
        sheet.paste(tile,(n*240,45)); d.text((n*240+10,12),labels[n],font=font(17),fill='white')
    frames.append(sheet)
frames[0].save(out/'weather-intensity-v3.gif',save_all=True,append_images=frames[1:],duration=110,loop=0)
for source in sources:source.close()
