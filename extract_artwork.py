"""Mechanically split generated sprite sheets into independently loadable assets."""
import argparse
from pathlib import Path
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('source');parser.add_argument('target');parser.add_argument('--cols',type=int,required=True)
parser.add_argument('--rows',type=int,required=True);parser.add_argument('--names',nargs='+',required=True)
args=parser.parse_args()
assert len(args.names)==args.cols*args.rows
target=Path(args.target);target.mkdir(parents=True,exist_ok=True)
with Image.open(args.source) as sheet:
    sheet=sheet.convert('RGBA');w,h=sheet.size
    for n,name in enumerate(args.names):
        col=n%args.cols;row=n//args.cols
        tile=sheet.crop((round(col*w/args.cols),round(row*h/args.rows),round((col+1)*w/args.cols),round((row+1)*h/args.rows)))
        bbox=tile.getchannel('A').getbbox()
        assert bbox, name
        tile.crop(bbox).save(target/f'{name}.png')
print('Extracted',len(args.names),'transparent assets')
