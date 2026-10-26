"""Reusable contact sheet for independent single-image angle files."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from .geometry import ANGLES

def make_contact_sheet(root, columns=3, cell=(380,420)):
    root=Path(root)
    pad, heading=18,35
    rows=(len(ANGLES)+columns-1)//columns
    out=Image.new('RGB',(columns*(cell[0]+pad)+pad,rows*(cell[1]+heading+pad)+pad),(240,241,243))
    draw=ImageDraw.Draw(out)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
    for idx,a in enumerate(ANGLES):
        p=root/'images'/f'{a:03d}_clockwise.png'
        with Image.open(p) as im:
            thumb=ImageOps.contain(im.convert('RGB'),cell,method=Image.Resampling.LANCZOS)
        x=pad+(idx%columns)*(cell[0]+pad)
        y=pad+(idx//columns)*(cell[1]+heading+pad)
        draw.text((x,y),f'{a:03d}° clockwise'+('  [original]' if a in (0,60) else '  [atlas]'),fill=(32,38,45),font=font)
        ox=x+(cell[0]-thumb.width)//2
        oy=y+heading+(cell[1]-thumb.height)//2
        out.paste(thumb,(ox,oy))
    dst=root/'previews'/'all_angles_contact_sheet.png';dst.parent.mkdir(exist_ok=True)
    out.save(dst)
    return dst
