#!/bin/sh
# Creates nro/source/ as links to the files listed in sources.txt.
# Usage: sh link-sources.sh <patched melee-unlocked checkout>
set -e
MU=$(cd "$1" && pwd); HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$HERE/source"
while read -r name path; do
  case "$path" in gen/*) src="$HERE/$path" ;; *) src="$MU/$path" ;; esac
  ln -sf "$src" "$HERE/source/$name"
done < "$HERE/sources.txt"
