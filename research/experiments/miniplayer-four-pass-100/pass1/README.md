# Pass 1: separate shoulders and wider colored rim

The complete candidate improves compact tone and artwork, but expanded becomes too light. Its combined normalized score is 0.98466 against the previous proposal's 1.0. The candidate remains held after visual review; the working model is unchanged.

[Interactive comparisons](../../../../guide/miniplayer-four-pass.md) · [Exact recipe](final-recipe.json) · [Stage choices](choices.json) · [Independent replay](verification.json).

## Results

| Reference | Previous E | Candidate E | Interpretation |
| --- | ---: | ---: | --- |
| Expanded A | 9.5068 | 12.9747 | Body and rim worsen; artwork improves. |
| Expanded B | 5.4896 | 9.7445 | Body and rim worsen; artwork improves. |
| Compact A | 16.4327 | 13.2608 | Tone, rim and artwork improve; SSIM falls. |
| Compact B | 16.3892 | 12.3132 | Tone, rim and artwork improve; SSIM falls. |

The combined score equally weights baseline-normalized glass, rim, exterior and artwork errors across four references. It does not conceal the expanded regressions. Original partial and foreground guards remain in every metric record.

## All stages

| Stage | Outcome |
| --- | --- |
| Registration and refraction | One shared tip/shoulder candidate; both native grids and all source proofs pass. |
| Incident blur | Three widths assessed. The widest scores best numerically; visible excess softness remains a concern. |
| Color | Three shared fixed responses assessed. Lightening helps compact but harms expanded. |
| Outline | Three plateau/chroma combinations assessed. The narrowest combination wins; width and chroma are confounded. |
| Shadow | Three localized downward Gaussian fields assessed. The widest reduces exterior error on all four references. |
| Artwork | Three shared transforms assessed. Scale 0.94, upward shift 3 and radius 20 give the lowest artwork error. |
| Verification | Four completed and pre-foreground images, metrics and original guard decisions replay exactly. |
| Dispersion | Excluded explicitly. |

The selected rim plateau and fade are each two native pixels. Artwork dimensions and boxes are rounded to the original integer raster convention; centered placement can differ by half a pixel. The original asset and scoring boxes stay fixed.

Both full comparison sheets for each member were inspected. Expanded A's yellow edge remains too pale relative to its reference, and its source returns remain misplaced. Compact gains brightness, but its returned structure and cap details remain wrong. No full-fidelity claim follows.

## Controls and recovery

The shoulder coordinate passes actual-gradient, mirror, unit-index, physical-scale and independent support-maximum checks. A separate area calculation agrees with full-pixel quadrature. Expanded and compact rim integration require order 32; successive differences stay below 0.000001.

The initial control-query limit was exceeded and remains disclosed. A zero-alpha display control failed before outline candidates. Native-pixel projection exposed a units-dependent residual check; normalized projection repairs it without repeating the native grid.

The initial angular area-reference rule failed its own convergence test before pixel integration. A separate analytic-base correction then verified area. Neither failure changed tolerances or scientific arrays.

The four final replays completed successfully before optional diagnostic JSON serialization rejected an unavailable value. A separate saved-output diagnostic records unavailable samples as null; no compositor or score was repeated.

All clocks, initial failures, cumulative ledgers and supplemental setup allowances remain preserved. Previous studies, masks and source bytes are unchanged.

## Next question

Reduce the shoulder perturbation and preserve the white endpoint while lightening darker colors. Test chroma independently of width. Retain the useful artwork correction, then check shadow localization against the fixed before/after observations.
