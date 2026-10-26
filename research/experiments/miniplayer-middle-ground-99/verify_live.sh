#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == worker ]]; then
  base=$2; revision=$3; folder=$4; asset=$5; expected=$6
  name=${asset##*/}
  curl --fail --silent --show-error --max-time 45 "$base$asset?verify=$revision" -o "$folder/$name"
  actual=$(sha256sum "$folder/$name"); actual=${actual%% *}
  [[ "$actual" == "$expected" ]] || { echo "Hash mismatch: $asset" >&2; exit 1; }
  jq -n --arg path "$asset" --arg sha256 "$actual" '{path:$path,sha256:$sha256}' > "$folder/$name.json"
  exit 0
fi
revision=$1
base=https://anastaci1a.github.io/liquid-glass/
packet=research/experiments/miniplayer-middle-ground-99
folder=$(mktemp -d /tmp/liquid-glass-live99-XXXXXX)
curl --fail --silent --show-error --max-time 45 "${base}miniplayer-middle-ground.html?verify=$revision" -o "$folder/page.html"
rg -q 'Incident blur remains included' "$folder/page.html"
rg -q 'middle99-compact-b-final.png' "$folder/page.html"
jq -r '.panels[]|[.asset,.sha256]|@tsv' "$packet/publication-panels.json" | xargs -n2 -P6 bash "$0" worker "$base" "$revision" "$folder"
pagehash=$(sha256sum "$folder/page.html"); pagehash=${pagehash%% *}
jq -s --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg revision "$revision" --arg page "${base}miniplayer-middle-ground.html" --arg page_sha256 "$pagehash" '{verified_at:$at,deployment_commit:$revision,page:$page,page_sha256:$page_sha256,all_60_assets_exact:(length==60),assets:.,scientific_evaluations:0}' "$folder"/*.png.json > "$packet/live-publication.json"
jq -e '.all_60_assets_exact' "$packet/live-publication.json"
echo 'PASS live page and all 60 asset hashes'
