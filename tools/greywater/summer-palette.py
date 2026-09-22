#!/usr/bin/env python3
"""Create Greywater's terrain-only summer palette from an installed RA palette.
Usage: python3 tools/greywater/summer-palette.py INPUT.pal OUTPUT.pal
The untouched indices preserve water, roads, effects and reserved shadow colors.
Values are native Westwood 6-bit RGB (0..63).
"""
from pathlib import Path
import sys

SUMMER = {
    23: (17, 22, 11),
    26: (19, 28, 11),
    27: (22, 28, 12),
    28: (18, 25, 13),
    29: (23, 29, 15),
    30: (25, 33, 16),
    36: (27, 33, 20),
    39: (30, 37, 20),
    40: (27, 36, 21),
    46: (31, 40, 23),
    48: (35, 41, 25),
    53: (36, 44, 24),
    54: (38, 44, 26),
    55: (39, 47, 29),
    60: (43, 49, 30),
}

def build(source):
    if len(source) != 768:
        raise ValueError('Expected a 256-color, 6-bit Westwood palette')
    palette = bytearray(source)
    for index, rgb in SUMMER.items():
        palette[index * 3:index * 3 + 3] = bytes(rgb)
    return bytes(palette)

if __name__ == '__main__':
    Path(sys.argv[2]).write_bytes(build(Path(sys.argv[1]).read_bytes()))
