# One miniplayer model: expanded to compact without fitting

**The compact observation uses the exact selected expanded glass model, shortened only.** Both expanded references replay pixel-exactly from the canonical configuration. The unfitted compact pair passes original paired guards and source support. One frozen local boundary cohort regresses; no compact-specific adjustment is made.

| Evidence | Record |
| --- | --- |
| Required shared family | [Canonical configuration](../../../reconstruction/families/music-mini-player.json) |
| Length-only construction | [Shared factory](../../../reconstruction/music_miniplayer_family.py) |
| Declared clock and caps | [Protocol](protocol.json) |
| Expanded pixel-exact identities | [Zero controls](expanded-zero-controls.json) |
| Compact source-first proof | [Proof](source-proof-FIRST.json) |
| Shared-renderer parity | [Four patches](parity.json) |
| Complete transfer | [Result](result.json) |
| Exact parameter inheritance | [Family verification](family-verification.json) |
| Frozen boundary and score-order disclosure | [Saved validation](saved-validation.json) |

## Exact family requirement

One JSON configuration supplies the height controls, knots, minor half-extent, corner radius, corner join, index, background distance, incident blur, encoded response and outline/shadow state. The factory exposes major half-length as its only variable shape parameter.

| Parameter | Expanded | Compact |
| --- | ---: | ---: |
| Major half-length, original units | 7.225022904390323 | 4.906563038095225 |
| Minor half-extent | 1.012503164339156 | Same |
| Corner radius | 1.0043663048754772 | Same |
| Corner smoothing width | 0 | Same |
| Actual height | Selected positive cubic spline | Same controls and knots |
| Index / background distance | 1.5 / 2.1 | Same |
| Incident Gaussian | 6.75 native pixels, radius 21 | Same |
| Gain / bias | 0.596189238519786 / 0.3290237590837732 | Same |
| AA / sampling | 2 by 2 / exact bilinear | Same |
| Output blur / generated shadow | Zero / zero | Same |
| Reflected illumination | Unresolved; none invented | Same |

Both cases use the same original normalization of 88.5 native pixels. No scale fit or unit-conversion adjustment is needed. Existing translation, source, artwork, glyph assets and styles remain frozen reference inputs; they are not glass-model parameters.

The prior compact harmonic profile and smoothed outline are historical. They are not retained as a compact-only exception. Future optical changes must revise and validate the shared family, rather than calibrate each size independently.

## Source and native correctness

Both source gates passed before any changed RGB sampling. Each covers 596,237 whole-body subrays and 724,065 required-union subrays, with zero unsupported samples. All original guards and four scored subrays outside the new outline remain included.

Every finite 43-by-43 incident-kernel footprint and bilinear corner is certified. No source extension, fill, mask change, registration search or target context is used. Availability is conditional temporal-mosaic support, not hidden photographic truth.

The single compact geometry grid is reused across the pair. All four small shared-renderer patches match exactly. Expanded identity controls use retained supported samples and the original foreground chain; they run no new expanded rays or source queries.

## Measurements and visible limits

| Reference | Prior separate geometric E | Shared-family E | Completed SSIM |
| --- | ---: | ---: | ---: |
| A | 43.579106 | 27.323624 | 0.954257 |
| B | 38.032338 | 26.359075 | 0.953124 |

Every original glass, rim, held, interior, E, SSIM, exterior and ten paired glyph/artwork guards improves or ties. Both source proofs pass, and actual clipping is zero. Historical empirical scores are a separate, closer image-fit record; this is not a comparison against them.

The body is visibly lighter and closer. Thin bright outline, cap lighting, background-feature placement and reflected returns remain wrong. The same family limitation now appears across both lengths instead of being hidden by a separate compact model.

![Reference A and unfitted compact family transfer](compact-a-comparison.png)

![Reference B and unfitted compact family transfer](compact-b-comparison.png)

These full native-width comparisons use 920 pixels per side, a 64-pixel caption and a two-pixel gutter. No HQ render, motion or optical enlargement was generated.

## Frozen boundary regression and scalar correction

The original glass masks remain unchanged. New predicted coverage leaves four partial glass pixels per reference; this is not the same cohort as the prior model's 22 partial pixels. Both cohorts remain reported, and all their pixels remain in original scores.

| Frozen prior partial-glass cohort | Prior RMSE | Shared transfer RMSE |
| --- | ---: | ---: |
| A, 22 pixels | 44.193752 | 48.286343 |
| B, 22 pixels | 60.964592 | 41.922668 |

A's local regression is retained. It is not waived by aggregate improvement or used to trigger independent compact tuning. No full-fidelity acceptance follows.

The initial new exterior scalar cast to Python float before multiplying, unlike the original compact expression. The saved validation restores the original arithmetic order without rerendering or altering the as-run record. Exterior pixels are bit-exact to the prior model; corrected RMSE ties at 10.550281525 and 15.072770119.

## Actual work and reproduction

One shared compact grid uses 883,200 rays; four parity patches add 256. Query instrumentation counts 8,834,560 geometry units across height, boundary, footprint and spline delegates. Four constructors process 1,121,600 reference-mask pixels.

There are two incident fields, four known-mask erosions, 1,766,912 RGB interpolation queries, two expanded cached identities and two compact composites. Four metric calls use 20 SSIM Gaussian operations and four metric erosions. Saved validation adds residual reductions only; there is no fit or repeated native attempt.

The [observation driver](observe.py) reuses existing shared tracing, sampling conventions, incident filtering, response and foreground infrastructure. The [saved validation](validate_saved.py) preserves the original exterior arithmetic and prior boundary cohort. Both refuse repeated outputs.

Inputs can be restored with the existing expanded and compact input restorers. They verify indexed hashes and preserve original cases. The family file is the active shared parameter source; frozen historical scripts retain their original inputs and evidence.

Status is an unfitted required-family transfer, pending independent replay and primary publication. No new material fit, full-pipeline pass, physical-radiance identification or per-control optical law is claimed.
