# Model review after switch revision4

- Ordinary kernels:9native screens plus7joint kernel/material steps. Best paired E reductions~.0116%; rejected. Increasing blur helps B while hurting A. Directional dispersion remained fixed. No supported ordinary-blur change.
- Global chromatic scaling:8native signed spread tests on the newly changed cap-depth map. A small positive spread helps A by.0448% and worsens B; stronger or opposite spreads do not qualify. This rejects the tested fixed-material family, not dispersion in Apple.
- Source-brightness rim response:8native joint material/response steps, existing public model with3shared neutral thin/broad terms. First candidate E reductions1.5975%/3.1359% failed exterior/crop review. Constrained nonnegative continuation independently accepted as revision5: reductions1.3844%/1.4607%; final recipe/replay/crops and source proofs in rev4-ambient-review. No geometry, ordinary blur, directional dispersion, source, pose or mask changes. This is ONE candidate, not8passes.

## Interpretation and limits

- A/B estimated source means have encoded luma.758766/.814351. A shared source-mean response can account for part of their different neutral rim brightness. This is material/context calibration, NOT improved lens curvature or a recovered Apple lighting law.
- Current response coefficients are positive. Together with positive achromatic material gains and gamma, this yields a sufficient monotonicity proof for uniform gray fields; clipping, Gaussian averaging and convex reflection preserve order. It does not prove behavior for arbitrary colored/spatial backdrop changes.
- Only two contexts constrain the response. Background estimation and activation deformation are unresolved confounds; no independent holdout. A future third observed context would test transfer rather than merely lower training error. Do not silently include such a source in fitting or change the frozen epoch.
- Dark-rim/color-fringe errors need continued inspection. Do not interpret gain in an aggregate image score as a resolution of all crop defects.
- Revision5 is published at64b970e with explicit crop/source limits. Next controlled test compares spectral-map plus material against material-only fitting; the control settles at less than.0001% improvement, far below the pass threshold. This separates any actual spectral improvement from remaining material adjustment.
