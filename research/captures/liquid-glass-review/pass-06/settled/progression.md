# Playback score progression

All rows below were **re-scored from frozen PNG outputs**, using the same native Apple frame, glass mask and eroded icon mask. No model was refitted. Lower RGB error is better; higher SSIM is better. SSIM is not a literal matching percentage.

| Stage | Glass RGB error ↓ | Rim RGB error ↓ | SSIM ↑ | Icon RGB error ↓ |
| --- | ---: | ---: | ---: | ---: |
| [First published HD fit](https://github.com/anastaci1a/localica/commit/7a8061b0f554adc2edb072b24238c078461ab972) | 10.18 | 11.96 | 0.9577 | — |
| [Corrected HD fit](https://github.com/anastaci1a/localica/commit/b1636bb56893eedc437f4800108fccedb01ffc6d) | 8.62 | 11.69 | 0.9434 | — |
| [Pass 01](../../pass-01/README.md) | 8.69 | 11.79 | 0.9477 | — |
| [Pass 02](../../pass-02/README.md) | 8.69 | 11.79 | 0.9477 | 3.50 |
| [Pass 03](../../pass-03/README.md) | 8.69 | 11.79 | 0.9477 | 3.50 |
| [Pass 04](../../pass-04/README.md) | 8.68 | 11.85 | 0.9456 | 3.08 |
| [Pass 05](../../pass-05/README.md) | 8.06 | 11.11 | 0.9738 | 3.20 |
| [Pass 06 example](../README.md) | 8.07 | 11.14 | 0.9730 | 3.24 |
| **Settled final** | 8.08 | 11.15 | 0.9724 | 3.24 |

- Glass error fell about **20.6%** from the first published HD fit to the settled result. Most of the recent numerical improvement arrived with the post-refraction filtering in pass 05. The settled result uses the chosen lower lens blur and revised icon treatment, giving slightly higher error than that particular pass-05 candidate.
- Passes 02–03 did not revise the playback lens; pass 02 introduced independently calculated icon shading. Pass 03 explored other shapes.
- Early icon colors were copied from Apple or replaced with an unrelated flat drawing. They are marked **—**, not counted as zero-error successes. From pass 02 onward the icon score measures independently calculated interior colors on the same eroded mask.
- Early published input/material assumptions changed. Common output scoring makes the displayed comparisons consistent, but cannot isolate optical improvement from those earlier source/material changes. Small differences from older logs also reflect scoring the saved 8-bit output rather than floating-point material arrays.
- Pixel scores can favor smoothing and do not capture every motion artifact, local mismatch or subjective preference. The latest icon error is not the lowest; it incorporates the selected highlight/saturation/blur behavior. No independent-scene or temporal validation is implied.

## Earlier PR work without a reference-fit score

- [8d8015c](https://github.com/anastaci1a/localica/commit/8d8015c): Context/evidence audit. No measured playback-reference score was recorded.
- [754c7c8](https://github.com/anastaci1a/localica/commit/754c7c8): Lab presets and independent controls. No measured playback-reference score was recorded.
- [611e166](https://github.com/anastaci1a/localica/commit/611e166): Pressure/depth motion model. No measured playback-reference score was recorded.
- [2257181](https://github.com/anastaci1a/localica/commit/2257181): Portable equations / outer-rim correction. No measured playback-reference score was recorded.

## Other PR checkpoints

- [b6c56fe](https://github.com/anastaci1a/localica/commit/b6c56fe): Curvature/dispersion hypotheses; public comparison image not updated. Private pass01 scored separately.
- [99d182b](https://github.com/anastaci1a/localica/commit/99d182b): Slider input correction; no new playback image.
- [2c955cb](https://github.com/anastaci1a/localica/commit/2c955cb): Geometry/path verification; no separate accepted playback image.
- [610a589](https://github.com/anastaci1a/localica/commit/610a589): Radial-tail/icon equations; private pass05 scored separately.
- [e42fc48](https://github.com/anastaci1a/localica/commit/e42fc48): Proportional units / highlight taper; private pass06 scored separately.

[Complete score data and image provenance](progression.json) · [Settled preset and media](README.md)
