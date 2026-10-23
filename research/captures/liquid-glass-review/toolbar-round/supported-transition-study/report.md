# Supported-inner-profile proposal — one prospective improvement

Baseline is lead-accepted/published toolbar revision1 af5a5037b190491bc6a44bdd2037be536515948f, E6.998512744608. Native protocol/epoch remains d1d864eb6eb193d8b4b8ba4563dd89b667727059ad48d770602bb690e53f575d. Source, registration, masks, material, crown.10, source/postblur, tangent parameters and generated shadow remain fixed.

## Immutable proposal

`settlement/candidate-flat-recipe.json` is the simplest proposal for independent primary review. It folds ONLY three changes into existing normal B-spline coefficients4,5,6; no extra rendering primitive or model parameter is needed. Raw optimization recipe remains in `inner-2/recipe.json` and `settlement/recipe.json` for provenance.

| Metric | Accepted revision1 | Proposed inner profile |
| --- | ---: | ---: |
| E | 6.998512744608 | 6.870490597950 |
| Glass RMSE | 6.044535160065 | 5.843130588531 |
| Rim RMSE | 8.832458496094 | 8.813648223877 |
| Fixed exterior RMSE | 11.469442019668 | 11.469442017232 |

Native milestone and nonregression guards pass. Exterior difference is effectively unchanged numerically; do not claim a meaningful new shadow improvement. Gate evidence booleans remain false in agent result until independent primary review; agent counts0 new passes. Both starts and settlement are ONE inner-profile study, not three passes.

Final normalized coefficients4–6 are `[0.4906890136980095, 0.15007838846353588, -0.03588814119199657]`; deltas `[0.0028560286216676393, 0.021455782218208586, -0.03708205700570033]`, within±.04. Coefficients0–3 and all other recipe values are unchanged. These are signed inverse-map coefficients, not physical lens heights/Apple geometry. Negative coefficient6 remains explicit. The inherited total tensor field is empirical, not claimed integrable or Snell-derived.

## Convergence and support evidence

- Initial inner starts each used180 optimizer evaluations (181 recorded objective calls including initial evaluation), both hitting the budget. This limitation is preserved in study.json.
- A further bounded continuation from the best point is COMPLETE in settlement/result.json: Powell reports successful local termination after37 evaluations; selected vector and native pixels remain exactly identical to inner-2. This is local convergence within the stated bounds/quantized raster objective, not a global-optimum claim. No continuation gain was split into another pass.
- `basis-support.json`: coefficient4 support[.015,.45], coefficient5[.04,.75], coefficient6[.09,1] in normalized inward coordinate d/radius. Basis value/first/second derivatives are zero at both support endpoints. Outer coefficients were held fixed. The actual exterior guard was measured; support alone was not asserted to guarantee it after output filtering.
- Zero changes recover revision1 native pixels exactly for both tested variants. Flattening the selected deltas into the existing recipe also reproduces candidate native material bit-for-bit (`settlement/flat-recipe-verification.json`, max difference0). No runtime dependency on toolbar_supported_transition.py is required for this selected inner proposal.
- Same frozen target foreground exclusions remain; canonical glyphs and their rendering are primary-owned. No reference glyph pixels or target residual is inserted into the glass model.

## Rejected expanded variant

Two bounded expanded W/profile starts used exponent3–10, band.30–.75, coefficients2–4 deltas±.04. Seed1 hit260-evaluation budget; seed2 converged locally. Best native E6.965037565329/glass6.013668537140/rim8.793331146240/exterior11.469540897128: still below required improvement (E must<=6.963520180885), and exterior regresses. Reject both expanded variants. None was promoted or substituted for the baseline. Full vectors/objectives and bound-activity records are in study.json; source/shape/material/blur/masks unchanged.

## Handoff and continuing work

Read native scores in settlement/scores.json, proposal in settlement/candidate-flat-recipe.json, rendered material/coverage in settlement/material.npy and alpha.npy, clean native preview in settlement/clean-preview.png. All earlier per-start proposals and the preliminary outer-strip study are preserved separately. Primary is already independently verifying inner-2; settlement proves that immutable point is still the final selected proposal.

Next queue item2 runs an INDEPENDENT wider generated-shadow bracket on revision1, not on this unaccepted proposal. No dependent candidate will be stacked or shadow-only optical pass counted. Queue4 will assess a second real observation without changing scoring epoch or beginning paired fits; queue5 will supply final support/crop/replay evidence, with the required next-steps request before that final item. Standing queue acknowledged in ../progress.txt; no waiting for approval between rejected experiments or while immutable proposal verification runs. Explicit Ana pause overrides all continuation.

Residual E reduction against revision1: 1.829276467%. Not Apple accuracy.
