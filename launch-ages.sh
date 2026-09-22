#!/bin/sh
# Uses an installed .NET 10 SDK, or the workspace-local SDK from this setup.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v dotnet >/dev/null 2>&1; then
    DOTNET_ROOT="$(pwd)/../.openra-tools/dotnet"
    export DOTNET_ROOT
    PATH="$DOTNET_ROOT:$PATH"
    export PATH
fi
if ! command -v dotnet >/dev/null 2>&1; then
    echo 'Install .NET 10 SDK before launching OpenRA.' >&2
    exit 1
fi
if [ "${1:-}" = '--demo' ]; then
    shift
    set -- Launch.Map=ages-ironwood Launch.Bot=ages "$@"
fi
exec python3 ./tools/skirmish/run.py ./launch-game.sh Game.Mod=ages Graphics.Mode=Windowed Graphics.WindowedSize=1280,800 Game.ViewportEdgeScroll=false "$@"
