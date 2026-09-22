"""Build the symmetric, three-route Ironwood Crossroads skirmish map."""
from pathlib import Path
from collections import deque
import random,struct
root=Path(__file__).resolve().parents[2]
w,h=130,98
rng=random.Random(2709)
tiles={(x,y):(255,rng.randrange(16)) for x in range(w) for y in range(h)}
resources={}; trees=set()
# Dense central forest separates three broad lanes. Top/bottom map edges are sealed.
for x in range(59,71):
 for y in range(1,97):
  if not (19<=y<=29 or 42<=y<=56 or 69<=y<=79):trees.add((x,y))
# Soft organic edges, identical on both sides.
for x in range(53,59):
 for y in range(2,96):
  if y not in range(17,32) and y not in range(39,60) and y not in range(66,83) and rng.random()<.42:
   trees.update([(x,y),(129-x,y)])
# Woodland shelters behind the starting settlement, leaving the home ore open.
for x in range(4,33):
 for y in range(8,36):
  if ((x-14)/16)**2+((y-19)/13)**2<1 and rng.random()<.48:trees.update([(x,y),(129-x,y)])
# Dirt approaches converge on north/central/south crossings.
for lane in [24,49,74]:
 for x in range(28,102):
  for y in [lane-1,lane]:
   if (x,y) not in trees:tiles[x,y]=(228,0)
# Symmetric ore: safe home fields and two forward expansion fields per side.
ore=[(13,62,7),(116,62,7),(41,32,5),(88,32,5),(41,67,5),(88,67,5)]
for cx,cy,r in ore:
 for x in range(cx-r,cx+r+1):
  for y in range(cy-r,cy+r+1):
   if (x-cx)**2+(y-cy)**2<=r*r:resources[x,y]=(1,12)
# High value center can be approached from both sides; it never blocks the lanes.
for x in range(60,70):
 for y in range(44,55):
  if ((x-64.5)/5)**2+((y-49)/5.5)**2<1:resources[x,y]=(2,10)
assert not set(resources)&trees
# Validate foot/cavalry routes at tile level; actual engine paths are also tested in-game.
def connected(start,end):
 seen={start};q=deque([start])
 while q:
  x,y=q.popleft()
  if (x,y)==end:return True
  for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
   if 1<=p[0]<129 and 1<=p[1]<97 and p not in trees and p not in seen:seen.add(p);q.append(p)
 return False
for y in [24,49,74]:assert connected((20,49),(65,y)) and connected((109,49),(65,y))
for (x,y),value in resources.items():assert resources.get((129-x,y))==value
for x,y in trees:assert (129-x,y) in trees
b=bytearray(struct.pack('<BHHIII',2,w,h,17,0,17+3*w*h))
for x in range(w):
 for y in range(h):b+=struct.pack('<HB',*tiles[x,y])
for x in range(w):
 for y in range(h):b+=bytes(resources.get((x,y),(0,0)))
p=root/'mods/ages/maps/ages-ironwood';p.mkdir(exist_ok=True);(p/'map.bin').write_bytes(b)
s='''MapFormat: 12
RequiresMod: ages
Title: Ages - Ironwood Crossroads
Author: OpenRA Ages
Tileset: TEMPERAT
MapSize: 130,98
Bounds: 1,1,128,96
Visibility: Lobby
Categories: Conquest
Players:
	PlayerReference@Neutral:
		Name: Neutral
		OwnsWorld: True
		NonCombatant: True
		Faction: england
	PlayerReference@Creeps:
		Name: Creeps
		NonCombatant: True
		Faction: russia
	PlayerReference@Multi0:
		Name: Multi0
		Playable: True
		Faction: england
		Spawn: 1
	PlayerReference@Multi1:
		Name: Multi1
		Playable: True
		Faction: russia
		Spawn: 2
Actors:
	Spawn1: mpspawn
		Owner: Neutral
		Location: 20,49
	Spawn2: mpspawn
		Owner: Neutral
		Location: 109,49
'''
for i,(x,y,r) in enumerate(ore):s+=f'\tOre{i}: mine\n\t\tOwner: Neutral\n\t\tLocation: {x},{y}\n'
for i,x in enumerate([63,66]):s+=f'\tGems{i}: gmine\n\t\tOwner: Neutral\n\t\tLocation: {x},49\n'
# Tree origin is one tile north of its occupied cell (the RA tree footprint is __ x_).
for i,(x,y) in enumerate(sorted(trees)):
 s+=f'\tTree{i}: t0{1+((min(x,129-x)*7+y)%3)}\n\t\tOwner: Neutral\n\t\tLocation: {x},{y-1}\n'
(p/'map.yaml').write_text(s)
print(f'Ironwood: {len(trees)} trees, {len(resources)} resource cells, symmetric resource totals and all three routes connected.')
