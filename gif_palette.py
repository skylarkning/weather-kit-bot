"""Reserve GIF colours for the small, saturated Firefox mascot."""
from PIL import Image

def make_palette(frame, mascot):
    background=frame.convert('RGB').quantize(colors=160)
    # Sample only opaque sprite pixels; transparent RGB must not consume colours.
    pixels=[rgb[:3] for rgb in mascot.getdata() if rgb[3]>=240]
    sample=Image.new('RGB',(max(1,len(pixels)),1))
    sample.putdata(pixels or [(255,140,0)])
    fox=sample.quantize(colors=96)
    colours=background.getpalette()[:160*3]+fox.getpalette()[:96*3]
    palette=Image.new('P',(1,1));palette.putpalette(colours)
    return palette

def quantize_frame(frame, palette, mascot_mask):
    rgb=frame.convert('RGB')
    result=rgb.quantize(palette=palette,dither=Image.Dither.FLOYDSTEINBERG)
    # Direct nearest-colour mapping preserves clean mascot fills and gradients.
    clean=rgb.quantize(palette=palette,dither=Image.Dither.NONE)
    result.paste(clean,(0,0),mascot_mask)
    return result
