# Steeper front with an optically derived back

A positive, single-valued back is constructed behind the full canonical front spline. Its actual height derivative reproduces the physical correspondence prior at 1025 design nodes. This is a geometry construction, not a rendered improvement; dense forward tracing and source-first validation remain required.

## Visible hypothesis

The current half-height front gives a broad lower highlight and an incorrect cap/rim response. A steeper actual front changes the reflected direction distribution. The back is derived from the same physical correspondence prior to separate that front-normal change from arbitrary background displacement.

Only front scale changes from the [earlier construction](../miniplayer-inverse-geometry-17/README.md). The index remains 1.5, background distance 2.1 original length units, footprint and case poses unchanged. The same profile must serve both lengths. No image RGB or target score participates.

| Quantity | Result |
| --- | ---: |
| Front scale relative to canonical spline | 1 |
| Back maximum height | 0.010511176376289507 |
| Back global slope bound | 0.1380545527836483 |
| Minimum input-to-back radius derivative | 0.9299675071878281 |
| Maximum nodal direction/source error | 5.56 × 10⁻¹⁶ |

## Actual surface and proof

The [back profile](back-profile.json) is a cubic Hermite height. Its derivative comes from the same polynomial. Exact rational Bernstein controls certify nonnegative height and the stated height/slope bounds. No sampled-coordinate correction follows tracing.

The [solver](solver.json) reached the center in one solve. The [checkpoint](checkpoint.json), [nodal checks](nodal-validation.json), [design nodes](design-nodes.json) and [result](result.json) retain the actual branches and residuals. The old physical map is a design prior, not photographic truth.

The task starts at 09:37:46.872 UTC and ends at 09:52:46.872. The construction finished at 09:37:58.355; nodal validation finished at 09:39:10.532. The conservative accounting supplement includes the original Hermite endpoint evaluations, preserving the as-run ledger.

| Work | Conservative total |
| --- | ---: |
| ODE/right-hand-side evaluations | 3373 |
| Shared Snell points | 7801 |
| Profile scalar queries, including supplement | 14264 |
| Design nodes / bound segments | 1025 / 1024 |
| Native rays, image RGB reads, images and RGB fits | 0 |

## Next gate

A separately declared fixed forward observation must certify complete ordered paths and every required finite incident-kernel/bilinear source footprint before RGB. The construction alone does not establish global image correspondence, reflected scene support, outline fidelity or acceptance.
