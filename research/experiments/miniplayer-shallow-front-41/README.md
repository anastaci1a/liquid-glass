# Shallower front sag: positive inferred back

The fixed front sag of 0.02 original length units admits a positive, single-valued back. The actual nodal source residual is below 10⁻¹⁵. No image or target fit runs. This second perimeter-curvature construction follows the broad-contour result in [the first native trial](../miniplayer-perimeter-native-40/README.md).

| Quantity | Value |
| --- | ---: |
| Front depth | 0.02, or 1.77 native pixels |
| Front power | 33.76385521939009 |
| Unchanged front edge-slope bound | 0.6723414566078295 |
| Back maximum height | 0.11972296878953101 |
| Back slope bound | 0.5066573323652707 |

The existing bevel law supplies the front. Its power is determined by sag and the unchanged edge-slope anchor. The actual back is derived from the same physical correspondence prior as earlier trials. All derivatives come from those surfaces; no independent normal or image warp is introduced.

The [protocol](protocol.json) starts at 10:24:13.840 UTC and ends at 10:39:13.840. The [front recipe](front-geometry.json), [back profile](back-profile.json), [solver](solver.json), [checkpoint](checkpoint.json), [nodal validation](nodal-validation.json) and [result](result.json) retain exact values and branches.

Conservative totals are 3277 ODE/right-hand-side calls, 7609 shared Snell points, 23852 profile scalar queries, 1025 design nodes and 1024 bound segments. These include the retained Hermite endpoint/validation supplements. No new source or target RGB is read.

A separate fixed native observation must establish complete paths and finite source support before sampling. A positive nodal construction does not establish pixel-integrated thin-rim fidelity, observed lighting or full-model acceptance.
