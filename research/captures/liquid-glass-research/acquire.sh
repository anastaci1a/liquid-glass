#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
curl -fLsS https://developer.apple.com/tutorials/videos/com.apple.SwiftUI/liquid-glass-morph-views.mp4 -o morph.mp4
curl -fLsS https://developer.apple.com/tutorials/videos/com.apple.SwiftUI/liquid-glass-view-examples.mp4 -o examples.mp4
cat <<'SUMS' | sha256sum -c -
4feea1c34a97ae1a4853c8f38831b9c7579c739db2c1060b1f4b84d3082d3992  morph.mp4
c0818bee3abc322bda0b18eb281cf26b13c844432c91385558bf6b9b56daa6e0  examples.mp4
SUMS
mkdir -p morph frames
ffmpeg -v error -y -i morph.mp4 -vsync 0 morph/%04d.png
ffmpeg -v error -y -i examples.mp4 -vsync 0 frames/%04d.png
ffprobe -v error -select_streams v -show_entries frame=best_effort_timestamp_time,pkt_duration_time -of json morph.mp4 > morph-timestamps.json
ffprobe -v error -select_streams v -show_entries frame=best_effort_timestamp_time,pkt_duration_time -of json examples.mp4 > timestamps.json
