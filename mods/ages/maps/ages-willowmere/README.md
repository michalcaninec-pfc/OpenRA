# Willowmere

A compact, two-player Ages skirmish in the summer style of Greywater March.

- **72 × 64 playable cells:** one quarter of Greywater's area.
- Starts at (22,18) and (51,47), with clear hut and barracks footprints.
- A road between two main lakes forms the direct approach; open side routes lead past two small hamlets and exposed expansions.
- One home mine and one flank mine per side. Resource cells are exactly rotationally symmetric. Within 20 cells, each start has 93 ore cells with total resource depth 1,116.
- A three-cell-wide connection remains open between bases. The shortest orthogonal route is 58 cells, versus 114 on Greywater.

Run `Play Willowmere.command` in the repository root for a skirmish against Ages AI, or choose **Ages - Willowmere** in the lobby.

Uses original RA TEMPERAT terrain and scenery, plus Greywater's map-local summer palette. No gameplay changes. Terrain scaffold: OpenRA Classic generator, seed 71, lakes, two rotational starts, 74 × 66 including the border. Starting locations, resource layout, forest pockets, hamlets and chapel were then authored for the smaller map.

OpenRA map refresh and YAML lint pass. Structural checks cover starting footprints, all four mines, mirrored resources, a three-cell-wide route and both flank waypoints. Competitive balance still needs match testing.

An isolated in-engine smoke test passed at tick 2,500: both starting armies spawned, both players harvested 3,000 resources, and a pikeman and field cannon each reached all four scripted route waypoints (with position assertions).
