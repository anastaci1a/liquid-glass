# Four complete miniplayer passes

Status: active. Four complete cycles share one ten-hour window. Dispersion is excluded by the current scope.

The starting experiment is [middle-ground99](../miniplayer-middle-ground-99/README.md). Earlier selected and experimental models remain immutable comparators.

## Schedule

Start: 2026-10-26 05:17:24 UTC. Final deadline: 2026-10-26 15:17:24 UTC.

| Pass | Deadline | Purpose |
| --- | --- | --- |
| 1 | 07:47:24 UTC | Establish contour, rim, localized shadow and artwork corrections. |
| 2 | 10:17:24 UTC | Refine promising ranges and peripheral transport. |
| 3 | 12:47:24 UTC | Check interactions across both lengths and references. |
| 4 | 15:17:24 UTC | Consolidate, verify nearby stability and publish final comparisons. |

Each cycle reserves 45 minutes for registration/refraction, 10 for incident blur, 10 for color, 25 for outline, 15 for shadow, 20 for foreground and 25 for verification/publication. Early closure does not reset clocks.

## Decision policy

Rank candidates by equally weighted, baseline-normalized category errors across all four references. Keep glass, rim, exterior shadow and artwork categories separate. Report original local guards and SSIM alongside ranking.

Visual improvement and improved combined ranking may justify a working-model update despite disclosed local regressions. Invalid geometry, unsupported required samples and numerical failures cannot qualify. Historical acceptance counts remain unchanged.

Each stage permits at most three substantive candidate sets before review. Failed candidates remain recorded; independent stages continue. Training excludes held pixels. Final reference review is not held-out validation.

## Required work

- Separate outward tip adjustment from inward diagonal shoulder adjustment with a smooth convex contour.
- Derive normals and transport from actual surfaces; test slightly stronger peripheral refraction.
- Retain incident blur and assess its width before refraction.
- Increase saturated rim plateau and smooth inward fade independently, preserving white inputs.
- Test a localized downward shadow only on uncovered contributions.
- Test shared artwork scale, upward placement and absolute corner radius.
- Reproduce outputs independently and inspect all four full images and native detail crops.
- Publish reference/result and previous/current sliders after each pass.

All optical parameters remain shared across lengths. Registration and foreground are separate measured inputs. Source availability remains conditional, rather than photographic ground truth.

## Reproducibility

Record each stage's actual clock, immutable inputs, controls, declared substantive limits, results and failures before closing it. Reuse certificates only when dependencies remain unchanged. Save durable failure records before numerical execution.

No helper is assigned. Verification belongs to the primary researcher. Latest feedback is retained locally verbatim and summarized in [the feedback record](../../feedback/miniplayer-four-pass.md).
