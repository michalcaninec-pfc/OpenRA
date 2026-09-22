# Ages: Pike to Steel

A playable Red Alert-derived skirmish prototype: start with a Gathering Hut,
Medieval Barracks and three Gatherers, build a medieval army, then buy the
Modern Age to unlock the normal Red Alert technology tree.

## Play

On this Mac, open **OpenRA Ages.app** next to this checkout, then
**Singleplayer → Skirmish**, select **Ages - Frontier**, and add **Ages AI**.
The normal lobby creates an Ages AI opponent by default.

From a terminal in the checkout:

```sh
./launch-ages.sh --demo     # Frontier, human vs Ages AI
./launch-ages.sh            # Main menu / normal skirmish lobby
```

Select the Infantry tab to train soldiers and Gatherers or research the age.
Select a Gatherer and right-click ore to gather; the Hut is the drop-off.
Select the Building tab to build another Hut or Barracks. After the age upgrade,
build a Power Plant, Ore Refinery and War Factory to reach modern vehicles.
Modern faction, power and technology prerequisites still apply.

## Prototype balance

| Item | Cost | Behavior |
| --- | ---: | --- |
| Gatherer | 110 | 20-bale capacity; ore and gems; returns to Hut or Refinery |
| Pikeman | 10 | 80 HP, 25 melee damage, 1.25-cell reach |
| Archer | 15 | 45 HP, 12 base arrow damage, four-cell range |
| Rider | 50 | 180 HP, 45 melee damage, speed 120 versus Pikeman 62 |
| Medieval Barracks | 100 | Trains the medieval army and researches the age |
| Gathering Hut | 150 | Drop-off, storage, Gatherer training and building production |
| Modern Age | 3000 | Permanent, once per player, paid through the normal production queue |

The starting treasury is $500. The medieval prices are approximately one tenth
of comparable basic infantry / light vehicle costs; there is no exact original
RA counterpart for an archer or mounted lancer. Gathering takes **40 ticks per
bale versus the Harvester's 4**, with equal speed and capacity. Travel, queuing
and unloading mean total income per minute is not exactly 1/10 in every layout.

Ages AI trains Gatherers and all three medieval troops, forms attack squads,
and saves for the upgrade. After advancing, it uses the stock RA base-building
and modern army logic. It receives no extra money or scripted upgrade.

## Where definitions live

- `mods/ages/mod.yaml`: independent mod assembled from RA assets plus Ages rules.
- `mods/ages/rules/medieval.yaml`: actors, start, economy and age upgrade.
- `mods/ages/rules/modern-gates.yaml`: preserves stock prerequisites and adds `modern.age`.
- `mods/ages/rules/ai.yaml`: harvesting, troop mix, savings and modern AI phase.
- `mods/ages/weapons/medieval.yaml`: arrow and cavalry attack; pike uses RA prototype's `PikeThrust`.
- `mods/ages/sequences/medieval.yaml`: mapping of unit actions and facings to sprite frames.
- `art/ages/prepare.py`: deterministic slicing, scaling, foot anchoring and player-palette encoding.
- `mods/ages/maps/ages-frontier`: two-player ore map with standard skirmish rules.
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
The generated art is an initial pass: Archer/Worker/Rider use two poses per
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
bot's natural economy and production. It repairs the human test buildings only
to keep the fixture alive long enough to observe the transition; this behavior
is absent from Frontier. It logs PASS lines and fails on wrong behavior/timeouts.
`Launch.Bot` is a small optional engine addition that fills the second playable
slot when launching a map directly. Normal skirmish lobby behavior is unchanged.

To reproduce art processing, install Pillow, extract `temperat.pal` from installed
RA content to `Support/pikeman-reference/` using `utility.sh ra --extract`, and run
`python3 art/ages/prepare.py`. Generated originals are retained under `art/ages/`.
Original Westwood game content remains local and is not committed to the fork.

Validated on macOS arm64 on 2026-09-22: clean build/lint, 508 engine tests passed
(two existing skips), and the in-game E2E test passed at tick 5000.
See `docs/ages-validation.txt` for the observed production, range and AI evidence.
