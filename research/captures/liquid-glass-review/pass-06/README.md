# Pass 06 — chosen lens and reduced icon highlights

[Pass 05 feedback](../pass-05/feedback.md) led to these changes. Slider and toolbar are unchanged; previous review images remain unchanged.

## Settled result

The final choice, full-HD video/GIF and progressive scores are in [settled/](settled/README.md). Earlier comparisons below remain as reviewed.

## Start here

- [02 — highlight / icon-blur grid](02-highlight-options.png). Columns reduce highlight progressively: **0, 0.25, 0.5, 1, 2**. Rows use **0, 2, 4px** of icon-color blur at the reference size. Apple repeats at the left; the reference itself is unchanged between rows.
- [08 — icon motion comparison](08-icon-motion-comparison.mp4). Same lens/background/path on both sides. Left: original pass04 icon response. Right: highlight reduction 0.5, dark saturation 0.2 and icon-color blur 2px at the reference size.
- [01 — complete comparison](01-playback-comparison.png). Apple, original pass04, chosen lens with original icon response, and the revised example.

The lens uses your **4.5 / gain 1** choice and **1.6px blur per 490px diameter** throughout. The icon amounts in the combined example/video are provisional; the grid lets you choose them independently.

## Other comparisons

| File | Contents |
| --- | --- |
| [03 — internal icon blur](03-icon-internal-blur.png) | 0, 1, 2, 4, 6px equivalents. Highlight reduction stays at 0.5 and dark saturation at 0.2. |
| [04 — dark saturation](04-dark-saturation.png) | Amounts 0, 0.1, 0.2, 0.3 near the diagonal edge. Highlight reduction stays at 0.5, icon-color blur at 2px. |
| [05 — rim crops](05-rim-crops.png) | Matching bottom-left, top-left and upper-right crops: Apple / pass04 / chosen lens. |
| [06 — dune detail](06-dune-detail.png) | Tiny central dune texture at 4×, including the chosen 1.6px lens blur. |
| [07 — moving lens](07-playback-motion.mp4) | Six-second preview of the revised example. |
| [09 — motion frames](09-motion-frames.png) | Four matching frames from the comparison clip. |

## Size and processing

All blur distances are proportions of the lens's **shorter dimension**, measured in the same units as its geometry. Pixel labels are equivalents for this 490px reference, not fixed values for every screen:

| Filter | Ratio to shorter dimension | 490px reference |
| --- | ---: | ---: |
| Existing source blur | 0.001020408 | 0.5px |
| Chosen glass blur after refraction/shading | 0.003265306 | 1.6px |
| Example icon-color blur | 0.004081633 | 2px |

- Geometry/displacement scales with the lens. Lighting is evaluated in normalized coordinates, including its thin-rim term; it does not keep a hidden fixed-pixel outline when resized.
- Icon pipeline: **original pass04 response → saturation weighted toward darker colors → highlight reduction → blur the calculated icon-color field → sharp silhouette coverage**.
- This icon blur happens **after** calculating its color, unlike the input-averaging trials in pass05. It filters neither the lens background nor the icon silhouette.
- Highlight reduction adds **no early white plateau**. It leaves channel values below 0.9 unchanged and preserves the white endpoint. The transfer is monotone throughout the tested/defined 0–4 strength range; larger values mean less highlight. A particular image can still fall short of pure white because its input is below that endpoint.
- Saturation boost decreases smoothly with brightness and vanishes at white. At a starting icon luminance of 0.9, amount 0.2 adds about 8.9% chroma; at 0.95 it adds about 2.2%. These are encoded-RGB controls, not recovered Apple lighting parameters.

## Findings and limitations

- Both highlight reduction **and internal blur** narrow the near-white area. Compare rows and columns independently. The example reaches about **1.08% near-white coverage**, versus about **1.86% in Apple**, under the same eroded-interior threshold; this is a diagnostic, not a visual acceptance score. Stronger reductions can remove that area entirely.
- The original independent RGB response is retained as requested. It has no general hue-order guarantee; motion remains important for exposing behavior outside the original pose. The new monotone highlight operator does not introduce order reversals by itself, but cannot repair any inherited from that original response.
- Geometry remains a radial inverse-map approximation. Gain 1 / width 4.5 is a chosen visual configuration, not a recovered solid. Its tested radial derivative has one sign change.
- Still-image exterior context remains the earlier estimate/retained reference context. The videos use the uncovered source image, omit the exterior shadow, and show translation without deformation.
- Videos are offline 30fps previews, **not** Android frame-time or Apple-motion validation. Both six-second / 180-frame H.264 clips decoded without errors.

## Evidence

- [Parameters and measurements](diagnostics.json)
- [Numerical controls](verification.json): scale covariance, lighting normalization and monotone highlight response, including unchanged reference-size lighting.
- [Video metadata](motion-diagnostics.json)
- [Full native renders](renders/)
- [Source script](scripts/playback-pass06.py), using existing sibling private reference inputs
- [File hashes](files.sha256)

The portable model documentation is updated on the research branch. The native app, main and the deployed lab remain unchanged. This folder stays private and editable over SMB.

[Feedback](feedback.md) · [All passes](../README.md)
