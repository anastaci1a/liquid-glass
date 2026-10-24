# Anchored perimeter curvature: positive back constructed

One perimeter-focused bevel front admits a positive, single-valued optically derived back. Its nodal Snell/source residuals are below 8 × 10⁻¹⁶. No image is rendered and no target coefficient is fitted. This construction follows the [three-direction review](../miniplayer-front-review-37/README.md).

## Fixed geometric anchors

| Quantity | Value or anchor |
| --- | --- |
| Front height at center | 0.0690909601310008; same as current working front |
| Front power | 9.773740343272607; determined by height and slope anchors |
| Front edge slope | 0.6723414566078295; canonical full-spline declared bound |
| Back maximum height | 0.07363728684913885 |
| Back global slope bound | 0.268132818542876 |
| Index / background distance | 1.5 / 2.1 original length units |

The power follows from the existing geometric anchors. It is not selected from target brightness or pixel errors. The actual front is the existing bevel law over the unchanged footprint. The actual back follows one optical ODE solve using the same physical correspondence prior as the earlier inverse designs.

The prior is an initialization constraint, not photographic truth. No empirical displacement is applied after tracing. Dense native correspondence, ordered paths, source support and visible fidelity remain untested for this new pair.

## Proof and timing

The [protocol](protocol.json) starts at 10:13:15.499 UTC and ends at 10:28:15.499. The [checkpoint](checkpoint.json), [solver](solver.json), [profile](back-profile.json), [front anchors](front-geometry.json), [nodal validation](nodal-validation.json) and [result](result.json) preserve exact branches and bounds.

The conservative total includes 3250 ODE/right-hand-side calls, 7555 shared Snell points, 23690 profile scalar queries, 1025 design nodes and 1024 bound segments. Original endpoint-query supplements are included separately from the immutable initial ledger.

A future single fixed forward observation must preserve the current common response, incident blur, light, foreground and all original guards. It must establish full finite-source support before RGB. A positive construction alone is not an outline improvement or model selection.
