"""Deterministically slice the generated sheet into OpenRA PNG frames.
The generated source has 7 rows (idle, 3 walk, 2 thrust, death), 8 facings.
Requires Pillow. Run from the repository root.
"""
from pathlib import Path
from PIL import Image, PngImagePlugin
source = Image.open(Path(__file__).with_name('source.png')).convert('RGBA')
source = source.resize((1280,1280), Image.Resampling.NEAREST)
rows = [(0, 174, 170), (174, 346, 338), (346, 524, 513),
        (524, 700, 688), (700, 869, 855), (869, 1067, 1028), (1080, 1240, 1208)]
frames = []
for top, bottom, feet in rows:
    for facing in range(8):
        tile = source.crop((160*facing, top, 160*(facing+1), bottom))
        tile = tile.resize((40, round((bottom-top)/4)), Image.Resampling.LANCZOS)
        frame = Image.new('RGBA', (48,48))
        frame.alpha_composite(tile, (4, 40-round((feet-top)/4)))
        frames.append(frame)
sheet=Image.new('RGBA',(48*8,48*7))
for i,frame in enumerate(frames): sheet.alpha_composite(frame,((i%8)*48,(i//8)*48))
meta=PngImagePlugin.PngInfo()
meta.add_text('FrameSize','48,48')
meta.add_text('FrameAmount','56')
meta.add_text('Offset','0,-16')
sheet.save('mods/ra/bits/pikeman.png', pnginfo=meta)
frames[4].save('mods/ra/bits/pikeman-icon.png')
# Facing-major sequence frame indices, as required by OpenRA.
s='pikeman:\n\tDefaults:\n\t\tFilename: pikeman.png\n\t\tScale: 0.7\n'
def seq(name, rows, facings=True, tick=100):
    global s
    ids=[r*8+f for f in range(8) for r in rows] if facings else [rows[0]*8+4]
    s+=f'\t{name}:\n\t\tFrames: '+', '.join(map(str,ids))+f'\n\t\tLength: {len(rows) if facings else 1}\n'
    if facings: s+='\t\tFacings: 8\n'
    s+=f'\t\tTick: {tick}\n'
seq('stand',[0]);seq('idle',[0]);seq('run',[1,2,3,2],tick=100)
seq('stab',[5,4,0],tick=100)
for name in ['die1','die2','die3','die4','die5','die6','die-crushed']:
    seq(name,[6],facings=False,tick=1000)
s+='\ticon:\n\t\tFilename: pikeman-icon.png\n\t\tScale: 1\n\t\tOffset: 0,0\n'
Path('mods/ra/sequences/pikeman.yaml').write_text(s)
print('Prepared 56 frames, 8 facings, idle/walk/thrust/death and build icon.')
