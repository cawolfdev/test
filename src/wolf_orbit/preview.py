"""Common contact-sheet rendering from already-saved standalone images."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from .geometry import ANGLES


def contact_sheet(image_files, output, columns=3, cell=(380,420), caption=None):
    """Reuses any existing images; never synthesizes a replacement frame."""
    image_files=[Path(p) for p in image_files]
    pad, heading=18,35
    rows=(len(image_files)+columns-1)//columns
    output=Path(output)
    out=Image.new('RGB',(columns*(cell[0]+pad)+pad,rows*(cell[1]+heading+pad)+pad),(240,241,243))
    draw=ImageDraw.Draw(out)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    for idx,p in enumerate(image_files):
        with Image.open(p) as im:
            thumb=ImageOps.contain(im.convert('RGB'),cell,method=Image.Resampling.LANCZOS)
        x=pad+(idx%columns)*(cell[0]+pad)
        y=pad+(idx//columns)*(cell[1]+heading+pad)
        text=caption(idx,p) if caption else p.stem
        draw.text((x,y),text,fill=(32,38,45),font=font)
        ox=x+(cell[0]-thumb.width)//2
        oy=y+heading+(cell[1]-thumb.height)//2
        out.paste(thumb,(ox,oy))
    output.parent.mkdir(parents=True,exist_ok=True)
    out.save(output)
    return output


def make_contact_sheet(root):
    root=Path(root)
    return contact_sheet(
        [root/'images'/f'{a:03d}_clockwise.png' for a in ANGLES],
        root/'previews'/'all_angles_contact_sheet.png',
        caption=lambda idx,p:f'{ANGLES[idx]:03d}° clockwise  '+ ('[original]' if ANGLES[idx] in (0,60) else '[atlas]'))


def make_proxy_contact_sheet(root):
    root=Path(root)
    return contact_sheet(
        [root/'mocks'/'proxy_3d'/f'{a:03d}_pose_proxy.png' for a in ANGLES],
        root/'previews'/'fixed_pose_geometry_proxies.png',
        caption=lambda idx,p:f'Camera azimuth {ANGLES[idx]:03d}°  [geometry proxy]')
