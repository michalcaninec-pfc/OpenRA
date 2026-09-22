"""Pack the generated tower into the existing RA player-palette pipeline."""
from pathlib import Path
from PIL import Image, PngImagePlugin
import runpy
root = Path(__file__).resolve().parents[2]
indexed = runpy.run_path(str(Path(__file__).with_name('prepare.py')))['indexed_sprite']
source = Image.open(Path(__file__).with_name('watchtower-source-v2.png')).convert('RGBA')
box = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox()
source = source.crop(box)
source.thumbnail((42, 52), Image.Resampling.LANCZOS)
meta = PngImagePlugin.PngInfo()
meta.add_text('Offset', f'0,{12-source.height//2}')
indexed(source).save(root / 'mods/ages/bits/watchtower.png', pnginfo=meta, transparency=0)
icon = source.copy()
icon.thumbnail((58, 44), Image.Resampling.LANCZOS)
canvas = Image.new('RGBA', (64, 48))
canvas.alpha_composite(icon, ((64-icon.width)//2, (48-icon.height)//2))
canvas.save(root / 'mods/ages/bits/watchtower-icon.png')
print('Watchtower sprite:', source.size)
