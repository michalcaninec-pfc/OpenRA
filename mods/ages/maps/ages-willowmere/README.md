# Willowmere

A compact, two-player Ages skirmish in the summer style of Greywater March.

- **72 × 64 playable cells:** one quarter of Greywater's area.
- Starts at (22,18) and (51,47), with clear hut and barracks footprints.
- A road between two main lakes forms the direct approach; open side routes lead past two small hamlets and exposed expansions.
- One home mine and one flank mine per side. Resource cells are exactly rotationally symmetric. Within 20 cells, each start has 93 ore cells with total resource depth 1,116.
- A three-cell-wide connection remains open between bases. The shortest orthogonal route is 58 cells, versus 114 on Greywater.

Run `Play Willowmere.command` in the repository root for a skirmish against Ages AI, or choose **Ages - Willowmere** in the lobby.

Uses original RA TEMPERAT terrain and scenery, plus Greywater's map-local summer palette. Map-local village capture and income rules are described below. Terrain scaffold: OpenRA Classic generator, seed 71, lakes, two rotational starts, 74 × 66 including the border. Starting locations, resource layout, forest pockets, hamlets and chapel were then authored for the smaller map.

OpenRA map refresh and YAML lint pass. Structural checks cover starting footprints, all four mines, mirrored resources, a three-cell-wide route and both flank waypoints. Competitive balance still needs match testing.

An isolated in-engine smoke test passed at tick 2,500: both starting armies spawned, both players harvested 3,000 resources, and a pikeman and field cannon each reached all four scripted route waypoints (with position assertions).

## Battle for the villages

Westmere and Eastmere each have eight neutral civilian buildings, a worn square and lanes connecting to the main road. Their capture circles are centered on their flag squares, at (14,28) and (59,37), with radius 5.5 cells. The animated flag and circle use the owning player’s color; civilian houses remain neutral scenery.

Move combat infantry or cavalry into the circle and hold it uncontested for eight seconds. Workers, engineers and vehicles cannot capture. Enemy eligible troops interrupt capture, reset progress and suspend income. Ownership persists after troops leave. A controlled, uncontested village generates $25 every ten game seconds ($150/minute), credited directly to cash. Capture gives no immediate bonus; hostile presence resets the payout timer. The flags are indestructible and do not count as bases for victory.

Every five game seconds, the Ages bot evaluates idle combat troops: defend a threatened owned village first, capture a neutral village next, then raid an enemy village. Neutral objectives can be taken by one or two troops; raids require at least three. A dispatch uses at most half the current ground army, preserves one idle guard near each owned village when available, and has a twenty-second per-objective cooldown. Within a priority it prefers nearby targets. Enemy counts are checked only near friendly troops or a friendly village; objective ownership is public. Normal army production and combat AI remain active, so this supplements rather than replaces the native squad manager. Progress and payout labels appear above the flag. Rules are confined to this map.

Regression fixture: `tools/greywater/villages-smoke.lua`, loaded after `villages.lua` in an isolated copy with fastest speed, default $500 and an idle Multi1 bot. Covers worker exclusion, capture delay, exact income, contested capture/income, enemy recapture, persistent control, independent capture of the second village, and a three-unit bot raid with three units kept in reserve.

`tools/greywater/villages-ai-smoke.lua` additionally tests the objective planner against actual in-engine actors: nearest neutral capture (2 troops), threatened village defense taking precedence (3 troops), and enemy raid (3 troops), each leaving a reserve from a six-unit army. These are tactical regression checks; full-match competitive balance remains unproven.
