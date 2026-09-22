# Greywater March

A 144 × 128, two-player Ages skirmish set among temperate lakes and rocky hills. Launch **Play Greywater.command** from the repository root to play against the Ages AI. Alternatively choose **Ages - Greywater March** in the skirmish lobby.

The trade road runs from the northwest settlement through the central lake saddle to the southeast settlement. The open approaches above and below the central lakes allow flanking instead of forcing every battle through one choke point. The old chapel and southern orchard mark those approaches. Two outer hamlets and two prospecting settlements give the edges a reason to exist.

The home ore fields support the early settlement. More exposed ore and gems reward expansion toward the northern and southern prospects. Resource placement is exactly rotationally symmetric; scenery is deliberately less rigid. Both headquarters and starting barracks have clear ground, and the road stops outside the starting footprints.

## Assets and construction

Uses the existing Red Alert TEMPERAT tileset, road segments, shorelines, cliffs, trees, civilian buildings and wooden fences. No additional downloadable textures or gameplay overrides. A map-local summer terrain palette lightens the grass and its transitions along roads, cliffs and shores; unit and UI palettes retain their normal colors. The terrain scaffold comes from OpenRA's Classic Map Generator (seed 53, lakes, two rotational starts); the central road, six settlements, forest pockets, orchard and resource cleanup were subsequently authored for this map. Original artwork remains in the installed game content archives.

## Validation

OpenRA map refresh and Ages YAML lint pass. Structural checks find 145 home resource cells (total depth 1,740) within 20 cells of either start, matching resource cells across the complete map, access to all 14 ore/gem mines, clear starting building footprints and a continuous three-cell-wide route between starts. The shortest orthogonal path between starts is 114 cells; northern, central and southern route waypoints are connected.

An isolated in-engine smoke test also passed: both headquarters, barracks and three workers spawned; a pikeman and field cannon completed the queued north–center–south route; both players harvested 4,500 resources by tick 4,000. The test used the actual Ages rules, with an idle opponent and faster game speed for observation.

These checks establish playability, not tournament balance. Match testing should focus on expansion timing, cannon control of the central saddle and the AI's ability to defend the longer flanks.

## Summer palette

`greywater-summer.pal` is generated from the installed `temperat.pal` using `tools/greywater/summer-palette.py`. Only 15 terrain palette entries change; reserved transparency/shadow colors and water blue entries are preserved. The map-local `rules.yaml` selects this palette without changing other maps. Shared terrain colors also affect some scenery details.
