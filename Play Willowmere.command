#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec ./launch-ages.sh Launch.Map=ages-willowmere Launch.Bot=ages "$@"
