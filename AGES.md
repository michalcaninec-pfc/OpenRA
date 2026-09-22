# Ages: Pike to Steel

A playable Red Alert-derived skirmish prototype: start with a Gathering Hub,
Medieval Barracks and three Gatherers, build a medieval army, research Gunpowder for muskets and field artillery, then
buy the Industrial Age to unlock the normal Red Alert technology tree.

## Play

On this Mac, open **OpenRA Ages.app** next to this checkout, then
**Singleplayer → Skirmish**, select **Ages - Ironwood Crossroads**, and add **Ages AI**.
The normal lobby creates an Ages AI opponent by default.

From a terminal in the checkout:

```sh
./launch-ages.sh --demo     # Ironwood, human vs Ages AI
./launch-ages.sh            # Main menu / normal skirmish lobby
```

The sidebar separates Buildings, Research, Medieval, Gunpowder and
Industrial forces. Every production card displays a name and the actual price.
Keyboard tabs: E Buildings, R Research, T Medieval, Y Gunpowder,
U Industrial Infantry; Ctrl+V/D/F/N selects vehicles/defenses/aircraft/ships.
Research Gunpowder ($1800) before Industrial Age ($4500). Locked future unit
cards stay hidden; medieval troops remain available as a cheap alternative.
Select a Gatherer and right-click ore to gather; the Hub is the drop-off.
Select the Building tab to build another Hub or Barracks. After the age upgrade,
build a Power Plant, Ore Refinery and War Factory to reach modern vehicles.
The Gathering Hub automatically fulfills Construction Yard requirements after
Industrial Age, including the starting hut. Its drop-off, storage, footprint and
production stay intact. Modern faction, barracks, power and technology
prerequisites still apply.

The Defenses tab is available from the medieval start: Watchtower $250 and
Wooden Palisade $20. Place wall endpoints along a straight line within eight
cells to connect them. Leave a passage for workers and troops; the tower needs
no power and fires arrows automatically.

## Prototype balance

| Item | Cost | Behavior |
| --- | ---: | --- |
| Gatherer | Included with hub | 8-bale capacity; ore and gems; returns to Hub or Refinery |
| Pikeman | 40 | 80 HP, 25 melee damage, 1.25-cell reach |
| Archer | 60 | 45 HP, 12 base arrow damage, four-cell range |
| Rider | 140 | 180 HP, 45 melee damage, speed 120 versus Pikeman 62 |
| Watchtower | 250 | 250 HP, arrow fire at six cells, seven-cell vision, no power required |
| Wooden Palisade | 20 | 150 HP per segment; connected wall placement |
| Medieval Barracks | 200 | Trains the medieval army and researches the age |
| Gathering Hub | 600 | 30 seconds in the shared building queue; spawns three Gatherers on completion |
| Musketeer | 120 | 55 HP, 28 damage, five-cell range; slow 65-tick reload |
| Field Cannon | 450 | 90 HP, splash damage, 2–9-cell range; slow and vulnerable up close |
| Rifle Infantry | 200 | Industrial tier, rapid fire; stays more expensive than basic medieval troops |
| Gunpowder Age | 1800 | Unlocks muskets and cannons; 750 base production ticks |
| Industrial Age | 4500 | Requires Gunpowder; unlocks the RA technology tree; 1250 base ticks |

The starting treasury is $500. Costs now reflect progression: Pikeman $40 →
Musketeer $120 → Rifle Infantry $200. Riders and artillery cost more because
they fill specialized roles. These are initial balance values, not a claim of
competitive balance. Gathering takes **160 ticks per bale versus the Harvester's 4**. Gatherers carry
8 bales instead of 20: one ore delivery pays $200, and gems $400. Compared with
the previous 40-tick Gatherer, raw mining throughput is reduced by 75%; smaller
loads add more travel per resource. Actual income also depends on travel and docking.

Ages AI builds two additional Gathering Hubs (nine Gatherers total) and trains all three medieval troops, forms attack squads,
and saves for Gunpowder, builds musketeers and field cannons, then saves for Industry.
After advancing, it uses the stock RA base-building
and modern army logic. It receives no extra money or scripted upgrade.

## Where definitions live

- `mods/ages/mod.yaml`: independent mod assembled from RA assets plus Ages rules.
- `mods/ages/rules/medieval.yaml`: actors, start, economy and age upgrade.
- `mods/ages/rules/modern-gates.yaml`: preserves stock prerequisites and adds `modern.age`.
- `mods/ages/rules/ai.yaml`: harvesting, troop mix, savings and modern AI phase.
- `mods/ages/weapons/medieval.yaml`: arrow and cavalry attack; pike uses RA prototype's `PikeThrust`.
- `mods/ages/sequences/medieval.yaml`: mapping of unit actions and facings to sprite frames.
- `art/ages/prepare.py`: deterministic slicing, scaling, foot anchoring and player-palette encoding.
- `mods/ages/maps/ages-ironwood`: symmetric 1v1, three forest passages, safe home ore, two forward expansions per side and contested central gems.
- `scripts/ages/build-ironwood.py`: deterministic map generator with symmetry/connectivity checks.
- `art/ages/synthesize-sounds.py`: deterministic procedural spear, bow and mining effects.
- `OpenRA.Mods.Common/Traits/Sound/SoundOnHarvest.cs`: positional, rate-limited mining sounds.
- `mods/ages/maps/ages-validation`: repeatable in-engine production/economy/combat/AI test.

An **actor** combines traits (movement, health, harvesting, production, attack).
Its armament names a **weapon**, which defines reach, reload, projectile and damage.
`RenderSprites` selects a sprite image; the **sequence** definition maps actions
such as `stand`, `run`, `attack` and `harvest` to frame indices and eight facings.
The PNG metadata carries frame size and origin. These are separate controls:
shrinking a sprite changes its appearance, not range, health or collision.

Foot infantry is normalized to roughly the original E1's 17-pixel body height.
The earlier Pikeman uses `Scale: 0.7`. Mounted units have a larger silhouette.
Ages PNGs use indexed RA player-palette colors, so cloth/flags follow owner color.
The generated art is an initial pass: Archer/Worker/Rider/Musketeer/Cannon use two poses per
facing, death uses the shared Pikeman collapse, and buildings use static art.
Directional consistency and animation polish remain art-production work.

## Build / validate

The checkout requires the OpenRA .NET SDK version and native dependencies.
This workspace has a local SDK in `../.openra-tools/dotnet` and installed RA
content in ignored `Support/Content/ra/v2/`.

```sh
make
./utility.sh ages --check-yaml
./launch-ages.sh Launch.Map=ages-validation Launch.Bot=ages
```

The validation map starts with the same $500 and real queues. It observes the
bot's natural economy and production. It repairs human test buildings and grants only human test workers damage
immunity to keep the fixture alive through concentrated fire; this behavior
is absent from playable skirmish maps. It logs PASS lines and fails on wrong behavior/timeouts.
`Launch.Bot` is a small optional engine addition that fills the second playable
slot when launching a map directly. Normal skirmish lobby behavior is unchanged.

To reproduce art processing, install Pillow, extract `temperat.pal` from installed
RA content to `Support/pikeman-reference/` using `utility.sh ra --extract`, and run
`python3 art/ages/prepare.py`. Generated originals are retained under `art/ages/`.
Original Westwood game content remains local and is not committed to the fork.

The v2 validation also checks three forest routes, all five medieval/gunpowder
weapons, separate production queues, paid age upgrades and AI progression.
Final v2 E2E passed at tick 7750, including automatic melee pursuit and nine-cell
cannon hits. Build/lint passed, with 508 engine tests passing and two existing
skips. See `docs/ages-validation-v2.txt` for the recorded run and QA limits.

## Sound

Spears/lances, bows and mining use short, quiet procedural WAV variants. Mining
sounds occur only on an actual harvested bale, at most about once per five
seconds per worker, with staggered timing and positional attenuation. Hidden
workers do not leak information through this effect. Muskets and artillery reuse
RA weapon reports; unit acknowledgements retain stock voices. The generator uses
only Python's standard library and fixed seeds. Runtime WAVs are committed.

## Controls and combat behavior

Medieval and gunpowder military units start in **Attack Anything**: idle melee units actively close
on nearby enemies instead of waiting for them to enter melee range. Hold Fire
and Defend remain available through the stance controls. Movement to empty
ground is still a move order; use Attack Move for an advance that engages enemies.

Custom mouse selection bounds cover the full sprites with a small margin. These
are separate from damage hit shapes and do not increase the units' collision or
splash vulnerability. Field Cannons reach nine cells, see seven and retain a
two-cell minimum range; spotters enable their full reach.

Defense regression: `Launch.Map=ages-defense-validation Launch.Bot=ages-defense-test`.
This dedicated fixture uses $5000 and scripted era tokens to isolate construction:
real production/placement of Watchtower, Palisade, Concrete Wall and Flame Tower,
automatic tower combat, and an existing hut gaining the conyard prerequisite.
Final run passed at tick 1700. See `docs/ages-defense-validation.txt`.

Camera controls: **W/A/S/D** pan up/left/down/right. The displaced commands
are **K** (select units by type), **G** (attack-move), **V** (stop), and **J**
(guard). These defaults apply only to Ages; unit stance shortcuts retain Alt.

Economy expansion uses Gathering Hubs only: individual Gatherer training and its
empty Economy tab are removed. The starting hub still has exactly three workers.
New hubs cost $600 and take 750 ticks (30 seconds at normal game speed), then spawn
three workers that automatically harvest. Building more hubs does not accelerate
the shared building queue. Selling a hub does not spawn an extra worker.
The AI pays for and places its hubs before Industry and can replace destroyed hubs;
automatic refinery selling is disabled to avoid selling hubs and repeatedly spawning workers.
Hub regression: `Launch.Map=ages-hub-validation Launch.Bot=ages`.
