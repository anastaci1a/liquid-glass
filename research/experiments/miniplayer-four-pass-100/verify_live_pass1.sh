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
packet=research/experiments/miniplayer-four-pass-100
folder=$(mktemp -d /tmp/liquid-glass-live100-XXXXXX)
curl --fail --silent --show-error --max-time 45 "${base}miniplayer-four-pass.html?verify=$revision" -o "$folder/page.html"
rg -q 'Miniplayer: four complete refinement passes' "$folder/page.html"
rg -q 'four100-p1-compact-b.png' "$folder/page.html"
jq -r '.panels[]|[.asset,.sha256]|@tsv' "$packet/publication-panels.json" | xargs -n2 -P6 bash "$0" worker "$base" "$revision" "$folder"
pagehash=$(sha256sum "$folder/page.html"); pagehash=${pagehash%% *}
jq -s --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg revision "$revision" --arg page "${base}miniplayer-four-pass.html" --arg page_sha256 "$pagehash" '{verified_at:$at,deployment_commit:$revision,page:$page,page_sha256:$page_sha256,all_assets_exact:(length==18),assets:.,scientific_evaluations:0}' "$folder"/*.png.json > "$packet/live-publication-pass1.json"
jq -e '.all_assets_exact' "$packet/live-publication-pass1.json"
echo 'PASS live page and all 18 asset hashes'
