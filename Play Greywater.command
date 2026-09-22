#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec ./launch-ages.sh Launch.Map=ages-greywater Launch.Bot=ages "$@"
