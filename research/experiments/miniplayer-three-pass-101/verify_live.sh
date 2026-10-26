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
packet=research/experiments/miniplayer-three-pass-101
folder=$(mktemp -d /tmp/liquid-glass-live101-XXXXXX)
curl --fail --silent --show-error --max-time 45 "${base}miniplayer-three-pass.html?verify=$revision" -o "$folder/page.html"
rg -q 'Miniplayer: three complete refinement passes' "$folder/page.html"
rg -q 'three101-p1-compact-b.png' "$folder/page.html"
jq -r '.panels[]|[.asset,.sha256]|@tsv' "$packet/publication-panels.json" | xargs -n2 -P6 bash "$0" worker "$base" "$revision" "$folder"
pagehash=$(sha256sum "$folder/page.html"); pagehash=${pagehash%% *}
expected=$(jq '.panels|length' "$packet/publication-panels.json")
passes=$(jq '.passes' "$packet/publication-panels.json")
jq -s --argjson expected "$expected" --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg revision "$revision" --arg page "${base}miniplayer-three-pass.html" --arg page_sha256 "$pagehash" '{verified_at:$at,deployment_commit:$revision,page:$page,page_sha256:$page_sha256,all_assets_exact:(length==$expected),assets:.,scientific_evaluations:0}' "$folder"/*.png.json > "$packet/live-publication-pass${passes}.json"
jq -e '.all_assets_exact' "$packet/live-publication-pass${passes}.json"
echo 'PASS live page and all declared asset hashes'
