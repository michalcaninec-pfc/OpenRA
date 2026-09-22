"""Pack generated gunpowder sprites into player-remapped PNGs."""
from pathlib import Path
from PIL import Image,PngImagePlugin
import runpy
root=Path(__file__).resolve().parents[2]
helpers=runpy.run_path(str(Path(__file__).with_name('prepare.py')))
indexed=helpers['indexed_sprite']
src=Image.open(Path(__file__).with_name('gunpowder-source.png')).convert('RGBA')
s=''
for name,row,scale in [('musketeer',0,.14),('fieldcannon',2,.17)]:
 frames=[]
 for r in [row,row+1]:
  for f in range(8):
   tile=src.crop((round(f*src.width/8),round(r*src.height/4),round((f+1)*src.width/8),round((r+1)*src.height/4)))
   box=tile.getbbox();tile=tile.crop(box);tile=tile.resize((max(1,round(tile.width*scale)),max(1,round(tile.height*scale))),Image.Resampling.LANCZOS)
   frame=Image.new('RGBA',(64,64));frame.alpha_composite(tile,((64-tile.width)//2,48-tile.height));frames.append(frame)
 sheet=Image.new('RGBA',(512,128))
 for i,frame in enumerate(frames):sheet.alpha_composite(frame,((i%8)*64,(i//8)*64))
 meta=PngImagePlugin.PngInfo();meta.add_text('FrameSize','64,64');meta.add_text('FrameAmount','16');meta.add_text('Offset','0,-16')
 indexed(sheet).save(root/f'mods/ages/bits/{name}.png',pnginfo=meta,transparency=0)
 icon=frames[4].crop(frames[4].getbbox());icon=icon.resize((round(icon.width*1.7),round(icon.height*1.7)),Image.Resampling.NEAREST);icon.thumbnail((58,44));canvas=Image.new('RGBA',(64,48));canvas.alpha_composite(icon,((64-icon.width)//2,(48-icon.height)//2));canvas.save(root/f'mods/ages/bits/{name}-icon.png')
 s+=f'{name}:\n\tDefaults:\n\t\tFilename: {name}.png\n'
 for seq,rs in [('stand',[0]),('idle',[0]),('run',[0]),('attack',[1,0])]:
  ids=[r*8+f for f in range(8) for r in rs];s+=f'\t{seq}:\n\t\tFrames: '+', '.join(map(str,ids))+f'\n\t\tLength: {len(rs)}\n\t\tFacings: 8\n\t\tTick: 110\n'
 for die in ['die1','die2','die3','die4','die5','die6','die-crushed']:
  s+=f'\t{die}:\n\t\tFilename: pikeman.png\n\t\tStart: 52\n\t\tScale: 0.7\n'
 s+=f'\ticon:\n\t\tFilename: {name}-icon.png\n\t\tOffset: 0,0\n'
(root/'mods/ages/sequences/gunpowder.yaml').write_text(s)
