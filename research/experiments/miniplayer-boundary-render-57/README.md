# Boundary integration is stable; the bright reference rim is still missing

Every actual geometric boundary pixel now receives a complete, source-certified area integral. Orders 8 and 16 agree to less than 0.001 of an eight-bit level over all rendered boundaries. The new images retain a thin, faint contour rather than the reference's brighter rim and cap illumination. Numerical correction does not establish optical fidelity.

| Reference | Old AA2 E | Area-order16 E | Maximum order8-to16 RGB difference, eight-bit levels |
| --- | ---: | ---: | ---: |
| Expanded A | 8.288537 | 8.284338 | 0.000836 |
| Expanded B | 6.920617 | 6.915364 | 0.000669 |
| Compact A | 21.576158 | 21.576145 | 0.000380 |
| Compact B | 20.676230 | 20.675815 | 0.000015 |

These E changes measure numerical integration under fixed optics. They are not a new surface improvement, guard waiver or scoring-epoch reset. The public working20 family remains selected; original AA2 figures, source, masks, registration and every earlier failure remain immutable.

## Inspectable comparisons

| Reference | Full comparison | Exact pre-foreground, completed and coverage arrays |
| --- | --- | --- |
| Expanded A | [Comparison](expanded-a-comparison.png) | [Order16](expanded-a-order16.npz) |
| Expanded B | [Comparison](expanded-b-comparison.png) | [Order16](expanded-b-order16.npz) |
| Compact A | [Comparison](compact-a-comparison.png) | [Order16](compact-a-order16.npz) |
| Compact B | [Comparison](compact-b-comparison.png) | [Order16](compact-b-order16.npz) |

All four full images were inspected. Cap light, white-return placement, body color and illumination distribution still differ. Exterior separation is absent because this frozen scene has shadow zero. The positive shadow50 result is a separate held underlay component, not silently included here.

## Common numerical policy

The [protocol](protocol.json) selects 5010 boundary pixels from the projected footprint alone. Both camera integration orders apply everywhere eligible, independently of reference residuals and guards. Unchanged interior/exterior pixels retain their old AA2 values exactly. Fractional coverage changes with the integration rule; original scoring masks never change.

The [shared positive rule](../../../reconstruction/pixel_quadrature.py) integrates the full clear pixel plus the covered glass-minus-clear correction. It uses actual front/back paths, surface-derived normals and finite panel48. All four cached complete/score identities are exact. No optical coefficient, lighting strength, blur width, foreground or source is retuned.

The [source-first ledger](source-FIRST.json) certifies all new paths and full radius 21 incident-kernel/bilinear footprints in both references before any changed field or RGB sampling. Direct clear contributions are also audited. Old unchanged interior support transfers through exact input/coordinate identity. Source availability remains conditional mosaic support, not hidden photographic truth.

## Budget and retention

The task traces 5507200 new rays, 220288000 surface points and 4405760000 conservative adapter units. Source auditing and RGB sampling each cover 22068880 points, with 88275520 mask lookups. Four incident fields, eight known erosions, four identities, eight candidates and twelve score calls remain within declared caps. All raw encoded clipping counts are zero.

First checkpoint and actual completion times are retained in [checkpoint](checkpoint.json) and [result](result.json). Full new temporary path arrays are not archived. Reproducible quadrature inputs, per-chunk source-proof hashes, completed arrays and original42 paths remain. This retention limit is explicit; a hash is not a replacement for an unavailable array.

Whole-image continuous convergence remains unproved because non-boundary pixels keep AA2. Later reflected power and real environment radiance are also unresolved. This result repairs a specific numerical defect and exposes the remaining modeling problem; it does not justify stronger illumination or a new surface without a discriminating physical hypothesis.

[Saved-metric regressions](saved-metric-regressions.json) disclose every worsening original scalar cohort and fixed crop against the old AA2 record. These numerical-protocol comparisons are not optical acceptance guards.
