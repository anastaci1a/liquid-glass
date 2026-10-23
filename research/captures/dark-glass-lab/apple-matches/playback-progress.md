- Ana's review adds targeted toolbar stroke-curvature/slight-blur checks; slider track-to-rim continuity and a separately reconstructed contact-shadow/blue-halo model; playback rim crops and background-dependent white-icon shading.
- Private review passes preserve unchanged originals. Playback baseline is an uncovered native-HD frame registered from 180s to 190s; 71 inliers, exposed-field mean channel error 1.42/255. It is not the original standalone photograph.
- Initial white-mask response reduces icon-interior RGB RMSE from 22.33 (white) / 8.15 (constant cream) to 3.47; same-frame withheld blocks 3.38. Zero added blur beats tested blurred variants. This is a fitted approximation, not an identified Apple shader; remaining gradient mismatch is visible.
- Existing comparisons copied reference glyph RGB and retained exterior context; those matching pixels were excluded from optical scores. New icon trials discard copied interior RGB. General exterior shadow/halo reconstruction remains open.
- Continuing on PR414; app/main/Pages unchanged.
— Codex
