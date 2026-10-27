#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == worker ]]; then
 base=$2;revision=$3;folder=$4;asset=$5;expected=$6;name=${asset##*/}
 curl --fail --silent --show-error --max-time 45 "$base$asset?verify=$revision" -o "$folder/$name"
 actual=$(sha256sum "$folder/$name");actual=${actual%% *};[[ "$actual" == "$expected" ]]
 jq -n --arg path "$asset" --arg sha256 "$actual" '{path:$path,sha256:$sha256}' > "$folder/$name.json"
 exit 0
fi
revision=$1;base=https://anastaci1a.github.io/liquid-glass/;packet=research/experiments/miniplayer-outline-range-112;folder=$(mktemp -d /tmp/liquid-glass-options-live-XXXXXX)
curl --fail --silent --show-error --max-time 45 "${base}miniplayer-outline-range.html?verify=$revision" -o "$folder/page.html"
rg -q 'outline-color' "$folder/page.html"
{ jq -r '.panels[]|[.asset,.sha256]|@tsv' "$packet/publication.json"; for asset in outline-range.js outline-range-sources.json guide-comparison.js; do hash=$(sha256sum "guide/$asset");printf '%s\t%s\n' "$asset" "${hash%% *}";done; } | xargs -n2 -P8 bash "$0" worker "$base" "$revision" "$folder"
jq -s --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg revision "$revision" '{verified_at:$at,deployment_commit:$revision,assets:.,all_assets_exact:(length==2643),scientific_evaluations:0}' "$folder"/*.png.json "$folder"/*.js.json "$folder"/*.json.json > "$packet/live-publication.json"
jq -e '.all_assets_exact' "$packet/live-publication.json"
echo 'PASS live dropdown page and2643 asset/data/script hashes'
