# Grazing quadrature: AA2 can exaggerate one edge pixel thirteenfold

Continuous integration gives unit reflectance 0.02523092 for expanded lower pixel 503, while the native AA2 estimate is 0.33802422. AA8 gives 0.01899835 and remains imperfect. The closed-surface highlight needs converged integration before brightness is interpreted. No selected reconstruction or native scoring protocol changes.

## Fixed numerical question

The [protocol](protocol.json) starts at 07:57:39.816 and ends at 08:07:39.816 UTC. All twelve cached AA2 pixel identities pass before adaptive integration. Geometry, index, pose phase and the unit-reflectance question remain fixed; no source, scene or material coefficient is fitted.

The straight body is invariant along horizontal position. Its pixel-area integral therefore reduces exactly to one vertical integral. The integrand evaluates the actual front root and level gradient, then shared Fresnel reflectance. It does not define an independent normal approximation.

$$
\overline R_j=\int_{j-\frac12}^{j+\frac12}R_{\mathrm{front}}(y)\,\mathrm d y.
$$

Outside the footprint there is no interface contribution. The measure-zero projected tangent has a one-sided reflectance limit for integration only; it is never reclassified as a regular traced ray. The original AA2 callback values match the saved native field within 1e-12.

## Pixel results

| Member/edge pixel | AA2 | AA8 | Adaptive integral |
| --- | ---: | ---: | ---: |
| Expanded upper 324 | 0.04611624 | 0.06357344 | 0.05543648 |
| Expanded lower 503 | 0.33802422 | 0.01899835 | 0.02523092 |
| Compact upper 583 | 0.03021012 | 0.02279455 | 0.03162772 |
| Compact lower 762 | 0.06632106 | 0.07669106 | 0.04971513 |

All twelve rows, including exterior zeros and interior comparisons, remain in the [result](result.json). The largest reported adaptive error is below 1.72e-9. The fixed absolute acceptance bound is 1e-7. No tolerance, subdivision limit, pixel selection or shape is changed after execution.

The native expanded lower edge lies unusually close to an AA2 subray. That point samples near-tangent reflectance and overstates the pixel average. Higher fixed sampling also remains sensitive to alignment. Continuous integration supplies a numerical reference for this unit-reflectance problem, not a new optical model.

## Relation to the earlier AA test

The [earlier patch diagnostic](../miniplayer-outline-sampling-24/README.md) used the finite-slope open geometry. Its small AA2/AA4 changes remain valid for that model. They do not transfer to the new closed surface, whose normal approaches a grazing angle in a subpixel band.

This distinguishes sampling error from material blur. Incident filtering, reference images and the selected body remain unchanged. A thin bright line in an under-integrated candidate cannot establish successful outline modeling.

## Work and decision

| Work | Actual |
| --- | ---: |
| AA2 identity pixels | 12 |
| AA8 diagnostic pixels | 12 |
| Pixel integral requests, including exterior zeros | 12 |
| Actual geometry callback points | 1380 |
| Conservative geometry delegate units | 27600 |
| Shared Fresnel points | 1326 |
| Source RGB queries, internal traces and fits | 0 |

[Checkpoint](checkpoint.json), [ledger](ledger.json) and [result](result.json) preserve ordering and actual counts. Camera samples are counted as geometry callbacks, not hidden inside a zero-work claim. Full source-dependent reflected RGB requires its own support and integration proof; these scalar integrals do not provide that proof.
