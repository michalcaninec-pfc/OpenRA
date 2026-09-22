"""Slice generated source art, normalize scale/feet, write OpenRA PNG sheets."""
from pathlib import Path
from PIL import Image, PngImagePlugin
ROOT=Path(__file__).resolve().parents[2]
source=Image.open(Path(__file__).with_name('units-source.png')).convert('RGBA')
rows=[(40,180),(190,345),(375,505),(530,665),(675,865),(875,1050)]
s=''
for unit,offset in [('archer',0),('worker',2),('rider',4)]:
 frames=[]
 for row in range(offset,offset+2):
  for f in range(8):
   im=source.crop((round(f*source.width/8),rows[row][0],round((f+1)*source.width/8),rows[row][1]))
   box=im.getbbox();im=im.crop(box)
   im=im.resize((max(1,round(im.width*.18)),max(1,round(im.height*.18))),Image.Resampling.LANCZOS)
   frame=Image.new('RGBA',(48,48));frame.alpha_composite(im,((48-im.width)//2,39-im.height));frames.append(frame)
 sheet=Image.new('RGBA',(384,96))
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,((i%8)*48,(i//8)*48))
 meta=PngImagePlugin.PngInfo();meta.add_text('FrameSize','48,48');meta.add_text('FrameAmount','16');meta.add_text('Offset','0,-15')
 sheet.save(ROOT/f'mods/ages/bits/{unit}.png',pnginfo=meta)
 icon=frames[4].getbbox();im=frames[4].crop(icon);im.thumbnail((48,42));canvas=Image.new('RGBA',(64,48));canvas.alpha_composite(im,((64-im.width)//2,(48-im.height)//2));canvas.save(ROOT/f'mods/ages/bits/{unit}-icon.png')
 s+=f'{unit}:\n\tDefaults:\n\t\tFilename: {unit}.png\n'
 for seq,rs in [('stand',[0]),('idle',[0]),('run',[0,1]),('attack',[1,0]),('harvest',[1,0])]:
  ids=[r*8+f for f in range(8) for r in rs];s+=f'\t{seq}:\n\t\tFrames: '+', '.join(map(str,ids))+f'\n\t\tLength: {len(rs)}\n\t\tFacings: 8\n\t\tTick: 160\n'
 for die in ['die1','die2','die3','die4','die5','die6','die-crushed']:
  # Shared existing pikeman collapse frame, not an upright unit on death.
  s+=f'\t{die}:\n\t\tFilename: pikeman.png\n\t\tStart: 52\n\t\tScale: 0.7\n'
 s+=f'\ticon:\n\t\tFilename: {unit}-icon.png\n\t\tOffset: 0,0\n'
source=Image.open(Path(__file__).with_name('buildings-source.png')).convert('RGBA')
for i,(name,width) in enumerate([('mbarracks',52),('mhut',74)]):
 im=source.crop((i*source.width//2,0,(i+1)*source.width//2,source.height));im=im.crop(im.getbbox());im=im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
 meta=PngImagePlugin.PngInfo();meta.add_text('Offset','0,-12')
 im.save(ROOT/f'mods/ages/bits/{name}.png',pnginfo=meta)
 icon=im.copy();icon.thumbnail((60,44));canvas=Image.new('RGBA',(64,48));canvas.alpha_composite(icon,((64-icon.width)//2,(48-icon.height)//2));canvas.save(ROOT/f'mods/ages/bits/{name}-icon.png')
 s+=f'{name}:\n\tDefaults:\n\t\tFilename: {name}.png\n'
 for seq in ['idle','damaged-idle','make','dead','build','damaged-build']:
  s+=f'\t{seq}:\n\t\tLength: 1\n'
 s+=f'\ticon:\n\t\tFilename: {name}-icon.png\n\t\tOffset: 0,0\n'
(ROOT/'mods/ages/sequences/medieval.yaml').write_text(s)

# Encode sprites in the engine's player palette so blue cloth becomes team color.
# The palette comes from the user's installed RA content, not from a new art source.
palette_path=ROOT/'Support/pikeman-reference/temperat.pal'
if not palette_path.exists():
 raise SystemExit('Extract temperat.pal into Support/pikeman-reference first; see AGES.md.')
palbytes=palette_path.read_bytes()
colors=[tuple(v*4 for v in palbytes[i:i+3]) for i in range(0,768,3)]
allowed=[i for i in range(1,256) if i not in [3,4] and not 80<=i<=95]
cache={}
def indexed_sprite(im):
 out=Image.new('P',im.size);out.putpalette([v for c in colors for v in c]);indices=[]
 for r,g,b,a in im.convert('RGBA').getdata():
  key=(r,g,b,a)
  if key not in cache:
   if a<100: idx=0
   elif b>r*1.3 and b>g*1.15 and b>35:
    idx=80+round(15*(1-min(1,b/255)))
   else: idx=min(allowed,key=lambda i:(colors[i][0]-r)**2+(colors[i][1]-g)**2+(colors[i][2]-b)**2)
   cache[key]=idx
  indices.append(cache[key])
 out.putdata(indices);return out
for name in ['archer','worker','rider','mbarracks','mhut','pikeman']:
 path=ROOT/f'mods/ages/bits/{name}.png'
 src=ROOT/'mods/ra/bits/pikeman.png' if name=='pikeman' else path
 im=Image.open(src);meta=PngImagePlugin.PngInfo()
 for k,v in im.info.items():
  if isinstance(v,str):meta.add_text(k,v)
 indexed_sprite(im).save(path,pnginfo=meta,transparency=0)
print('Prepared medieval sprites with RA player-palette team-color indices.')
