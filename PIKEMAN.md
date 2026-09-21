# Pikeman prototype

A medieval melee unit added to the Red Alert mod. No engine C# changes are required.

## Run

On this Mac, open `../OpenRA Pikeman.app`, or run:

```sh
./launch-pikeman.sh
./launch-pikeman.sh --demo
```

The demo starts **Pikeman Proving Grounds**, a skirmish with barracks, a starting pikeman company, a Rush AI opponent, and an automatic smoke test. Leave the first test fighter alone for 20 seconds. Test results appear in-game and in `Support/Logs/lua.log`. Extra stationary enemy targets appear after the checks.

In a normal skirmish, train **Pikeman** from either Allied or Soviet barracks. Alternatively select **Pikeman company** under starting units. Left-click selects; right-click moves or attacks. The infantry production tab includes the new icon immediately after Rifle Infantry.

Local .NET SDK and NuGet cache live in `../.openra-tools/`; game data and saves live in the ignored `Support/` directory. Other machines need .NET 10, `make`, and the usual Red Alert content installed via OpenRA. Original game content is not included in Git.

## How the unit works

| File | Responsibility |
|---|---|
| `mods/ra/rules/pikeman.yaml` | Actor traits: production, health, movement, targeting, animation and starting army |
| `mods/ra/weapons/pikeman.yaml` | Range, reload, target filters and damage |
| `mods/ra/sequences/pikeman.yaml` | Named sprite animations and direction/frame mapping |
| `mods/ra/bits/pikeman.png` | 56 frames in 8 facings, 48×48 pixels per frame |
| `mods/ra/mod.yaml` | Registers the new rules, sequences, weapons and PNG sprite loader |
| `mods/ra/maps/pikeman-proving-grounds/` | Playable skirmish demonstration and runtime checks |

`PIKEMAN` inherits `^Soldier`, then overrides its traits. `Armament` references `PikeThrust`; `WithInfantryBody` chooses `stand`, `run` and `stab`. There is no gun or garrison weapon, and `TakeCover` is removed so the pikeman stays upright.

`PikeThrust` uses the engine's invisible `InstantHit` with `TargetDamage`: one targeted ground actor is damaged, with no flying projectile or splash. Range `1c256` is 1.25 cells (1024 world units = one cell). Damage is 2500 internal health units, reload 25 ticks (one second at normal speed). Health is 8000, cost 120, speed 62. Armor reduces damage to vehicles and buildings; airborne actors are excluded. These are prototype balance values.

OpenRA traditionally uses indexed SHP assets. This prototype enables the existing `PngSheet` loader instead. PNG metadata declares `FrameSize`, `FrameAmount` and ground-anchor `Offset`. YAML `Frames` reorders the source's row-major layout into direction-major animation frames. `Facings: 8` selects direction, `Length` selects frames per direction, and `Tick` is the animation frame duration in milliseconds.

## Art

Generated with the built-in imagegen tool; source is `art/pikeman/source.png`. `python3 art/pikeman/prepare.py` (Pillow required) slices and scales the source, writes PNG metadata, and regenerates the sequences and icon. The generated sheet contains idle, three walk poses, two thrust poses and one corpse pose for each facing.

This is basic prototype art: tunics currently stay blue rather than remapping to player colors; voice lines use the existing infantry voices; death has a single pose. Ownership is still indicated by selection/health UI. See `art/pikeman/PROMPT.txt` for the generation prompt.
