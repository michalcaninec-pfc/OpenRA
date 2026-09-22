# Ages artwork

Original generated source atlases are retained here; `prepare.py` makes the small
runtime sprites in `mods/ages/bits`. Runtime PNGs are committed so playing does not
require image generation or Pillow.

Sources were generated with the built-in image generation tool. The tool does
not expose a selectable backend model, so these files are not labeled as a
verified Image 2.5 output. References: a locally extracted original Red Alert E1
frame (scale/camera reference) and the earlier generated Pikeman atlas (design).
The original game frame is not redistributed here.

Units prompt: transparent 8-column × 6-row atlas, directions N/NW/W/SW/S/SE/E/NE;
rows Archer idle, Archer bow attack, Worker idle, Worker mining, mounted Rider
idle, mounted Rider thrust. Muted pixel-art RTS camera; blue combat cloth, gray
steel, tiny figures suited to a 17-pixel infantry body. The generated cells are
manually bounded in prepare.py, then resized and anchored by the feet.

Buildings prompt: two isolated transparent buildings, small timber-and-stone
barracks with slate roof and spear racks; timber gathering hut with thatched
roof and ore baskets. Elevated Red Alert-like camera, blue banners, muted colors,
readable silhouettes at 52px / 74px wide. The camera/art is an approximation,
not a pixel-identical match to original Westwood assets.

Mechanical processing retains alpha while slicing/scaling, then encodes to the
installed RA player palette. Blue cloth maps to indices 80–95 for owner remap;
transparent pixels map to index 0. Icons stay RGBA. The source art remains intact.

Known prototype limits: only two poses for each new unit/facing, several similar
facings in the generated atlas, shared Pikeman death frame and static building
construction/damage frames. A polished art pass would add genuine walk cycles,
individual death/damage states and more consistent directional silhouettes.
