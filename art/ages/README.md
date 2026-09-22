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

## Gunpowder and sound pass

`gunpowder-source.png` is a generated 8-column × 4-row atlas using the existing
Ages units as a visual reference: musketeer idle/fire, field cannon idle/fire.
`prepare-gunpowder.py` slices, scales, anchors and indexes the atlas using the
same RA palette conversion. Infantry remains near stock infantry scale.

`synthesize-sounds.py` generates six deterministic mono 22.05 kHz WAV files:
two pike/lance swishes with impact, two bow twangs and two mining taps. No external
audio samples are embedded. Musket and cannon reports reference installed RA
content instead of copying it. Mining uses positional attenuation and a per-unit
cooldown. The voice acknowledgements are still the stock RA voices.

`watchtower-source-v2.png` is the revised, broader timber watchtower, using the
first watchtower and original buildings as references. `prepare-watchtower.py`
packs it to 41×52 px (original was 34×64 px) with remappable
blue cloth and a separate icon. It currently has static make/damage states.
Palisades reuse the installed game's WOOD wall sprites and connection frames.
