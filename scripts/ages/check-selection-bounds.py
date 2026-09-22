"""Check clickable rectangles against every standing facing of the shipped art."""
from pathlib import Path
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
rules = (ROOT / 'mods/ages/rules/medieval.yaml').read_text()
actors = dict(re.findall(r'^([A-Z][A-Z.]+):\n(.*?)(?=^\S|\Z)', rules, re.M | re.S))


def bounds_for(actor):
    body = actors[actor]
    match = re.search(r'\tSelectable:\n(?:\t\t[^\n]+\n)*?\t\tBounds: ([^\n]+)', body)
    if match:
        return tuple(int(n) for n in match[1].split(','))
    parent = re.search(r'\tInherits: ([^\n]+)', body)[1]
    return bounds_for(parent)


for actor, sprite, scale in [('PIKEMAN', 'pikeman', .7), ('ARCHER', 'archer', 1),
                              ('WORKER', 'worker', 1), ('RIDER', 'rider', 1),
                              ('MUSKETEER', 'musketeer', 1), ('FIELD.CANNON', 'fieldcannon', 1)]:
    image = Image.open(ROOT / f'mods/ages/bits/{sprite}.png')
    width, height = map(int, image.info['FrameSize'].split(','))
    ox, oy = map(int, image.info['Offset'].split(','))
    image = image.convert('RGBA')
    bw, bh, bx, by = bounds_for(actor)
    # Same integer conversion as Interactable.Bounds for RA's 24px / 1024 world units.
    bw, bh = bw * 24 // 1024, bh * 24 // 1024
    bx, by = int(bx * 24 / 1024), int(by * 24 / 1024)
    left, top = -(bw // 2) + bx, -(bh // 2) + by
    for facing in range(8):
        x = facing * width
        box = image.crop((x, 0, x + width, height)).getbbox()
        l, t, r, b = ((box[0] - width / 2 + ox) * scale,
                      (box[1] - height / 2 + oy) * scale,
                      (box[2] - width / 2 + ox) * scale,
                      (box[3] - height / 2 + oy) * scale)
        assert left <= l and top <= t and r <= left + bw and b <= top + bh, (actor, facing, box)
    print(f'{actor}: all 8 standing silhouettes inside {bw}x{bh}px clickable rectangle')
