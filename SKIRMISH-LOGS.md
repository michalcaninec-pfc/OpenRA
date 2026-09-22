# Local skirmish diagnostics

Launch normally with **Play Willowmere.command**, **Play Greywater.command**, or `launch-ages.sh`. The common launcher now records automatically. No background scheduler or upload is used. Launching the native `.app` directly bypasses recording unless it is invoked through `tools/skirmish/run.py`.

Each launcher run gets a unique directory in `Support/SkirmishLogs/`. Each match loaded inside that process gets a distinct match ID and its own files. Logs are local, ignored by git, and not automatically deleted.

- `latest.md`: current summary of the most recently launched session's latest match.
- `session.json`: start/end UTC, process exit code, command, git revision and dirty state.
- `source/`, `source.diff`, `source-manifest.json`: exact Ages rules/scripts, uncommitted tracked changes, rule/map hashes and compiled engine hashes.
- `engine.log`: complete stdout/stderr, including errors and Lua diagnostics.
- `match-<id>.jsonl`: structured match start/end, actor creation/removal, developer orders, snapshots, village events and AI candidate/dispatch decisions.
- `match-<id>.md`: automatic high-level analysis; `report.md` indexes all matches in the session.

Snapshots arrive every 250 simulation ticks (10 game seconds). Reports refresh while playing and when the process exits. A crash/forced exit without a `match_end` is explicitly classified as interrupted, not a loss or a completed match. Completed worlds report actual win/loss states. An abandoned running terminal/process can leave a session marked running; absence of a final event is never evidence of a win.

## Reading the latest game

```sh
python3 tools/skirmish/report.py --latest
# Optional live refresh while debugging:
python3 tools/skirmish/report.py --latest --follow
# Rebuild a particular session report:
python3 tools/skirmish/report.py Support/SkirmishLogs/<session>
```

For AI debugging, start with `latest.md`, then the relevant `match-*.jsonl` and `engine.log`. Always check revision, dirty patch, map identity, test map versus real skirmish, game result and cheat orders before comparing matches.

The summary includes economy, production queues, unit composition, kills/losses, technology timing, village income and captures, and objective-AI decisions. Sustained high cash with no production, large idle armies, and stationary units running movement activities are flagged as **diagnostic leads**, not proven bugs. The actor IDs and positions let us follow the same unit across snapshots and distinguish a failed objective dispatch from a unit later redirected by the normal squad manager. Village AI reports rejected candidates too: cooldown, insufficient idle budget or no useful target.

Village cash is reported separately because the Lua payout directly changes cash rather than the engine's Earned counter. Developer orders (including +5k), reveal state, fast build and all-tech state are recorded. An actor being removed is not automatically counted as killed: transports, capture and transformations can remove/re-add actors.

The recorder observes both players without changing game logic or RNG. It is not a live player-facing overlay; it contains information hidden by fog. Activity target data depends on what each engine activity exposes. Ten-second snapshots cannot capture every micro-order, short combat exchange or prove pathfinding failure. Existing engine replays remain in `Support/Replays`; this recorder does not copy or reassign them to matches.

## Validation

`python3 -m unittest discover -s tools/skirmish -p test_report.py` checks truncated logs, multiple matches, interrupted sessions, Lua event attribution, losses and cheats. Real-engine tests additionally verify start/snapshots, player economy/production/activity data, village AI events, an interrupted launcher and a natural win/loss ending. The telemetry trait is enabled only when `AGES_TELEMETRY=1` is set by the wrapper, and ignores editor/shellmap/replay worlds.
