# Search closed-oval TIR continuations: scene remains incomplete

**All 549 omitted TIR launches are followed through event 16, but missing radiance and a non-small retained tail still prevent a complete scene.** Every available transmitted branch is retained. The audit produces no RGB, filter, composite or image. Search geometry, source, selected material and historical counts remain unchanged.

## Fixed scope and clock

The [protocol](protocol.json) starts at 06:12:32.996 UTC and ends by 06:32:32.996 UTC, including versioning. It binds the exact geometry and all actual cached initial events from [closed oval 24](../agent-search-closed-oval-24/README.md). No new native grid or surface setting runs.

The body remains the radius-scaled zero-kappa ellipsoid, with original radius, half-height depth, index 1.5 and background plane at negative two original units. Original L is 89 native pixels. The corrected center, sources, masks, styles, incident width, accepted tone and shadow zero remain frozen.

Every launch is selected by its existing blocked flag, not by source color, power or target error. The immutable cache contains exactly 549 such launches. The [checkpoint](checkpoint.json) binds hashes, exact selected headers, mask semantics and all cached records before transport. Its selected decoded payload is 52,539,744 bytes, below 512 MiB.

## One actual solid and complete retained branches

The same shared `ClosedCircularOval` supplies every implicit root and gradient, with the approved radius chain rule. The convexity certificate from 24 remains applicable. New segments use only shared `next_convex_boundary`; directions and interface power use shared reflection, Snell and Fresnel primitives.

The first two encounters are cached front entry and back TIR. The initial front-reflected direction is also retained from 24, including its downward background role. The initial internally reflected continuation is computed from the actual cached back normal and inside direction. No cached intersection is retraced or assigned a fabricated bracket.

Every launch receives fourteen new ordered segments. All 549 reflected continuations run through every remaining event, even if their power becomes small. No threshold deletes a branch. Each available transmission is retained with its status and endpoint; rounded zero-weight transmissions would also remain recorded.

| Work | Actual | Cap |
| --- | ---: | ---: |
| Launch records | 549 | 600 |
| Encounters, including cached events | 8784 | 9000 |
| Cached initial encounters | 1098 | Included above |
| New ordered segments | 7686 | 8000 |
| Primitive level points | 322812 | 650000 |
| Conservative shared/delegate units | 2174104 | 4200000 |
| Indexed known-mask lookups | 13200 | 150000 |
| Selected decoded cache/mask bytes | 52539744 | 536870912 |
| RGB, filtering, composites, images and fits | 0 | 0 |

The static reservation is 80 level points and 510 delegate units per new segment, including nested levels. Initial primitive calculations and setup are additionally reserved. Level points are already included in delegate units; they are not added twice. One persistent ledger covers setup and every event. No old counter is reset.

## Meridional polarization and power

Axisymmetry and zero kappa preserve the initial meridional plane: positions, gradients and incident directions begin in that plane, and shared reflection/refraction remain linear combinations of its vectors. The fixed tangential s axis is defined from each cached launch. No position, normal or direction is projected back into the plane.

$$
\boldsymbol s=\frac{(-y,x,0)}{\sqrt{x^2+y^2}}.
$$

Both scalar polarization powers start at one half. Their products remain separate through all interfaces. At normal incidence the s/p reflectances agree, so the fixed basis remains admissible. This argument is specific to this axisymmetric meridional geometry, not arbitrary three-dimensional polarization transport.

$$
\begin{aligned}
W_{j,\mathrm{transmitted}}&=W_{j,\mathrm{incoming}}(1-R_j),\\
W_{j,\mathrm{continued}}&=W_{j,\mathrm{incoming}}R_j,
\qquad j\in\{s,p\}.
\end{aligned}
$$

Snell discriminants determine critical/TIR status. Reflectance equal to one alone is not used as a TIR label. Blocked branches retain their NaN transmitted directions and full reflected power. All finite vector norms and meridional residuals are checked without repair; actual brackets and level residuals are saved at each new event.

The largest componentwise partition error is 1.227e-16, below the declared 3.411e-13 guard. No partition is renormalized. The largest initial cached front-direction plane residual is 1.666e-16; its unit-length error is 4.441e-16. These are saved-array checks, not repeated optical evaluations.

## Where the first internal exit goes

The following counts concern the first available internal transmission after cached event two. They exclude the separate initial front reflection. Six launches still have no available transmitted exit through event 16; this does not establish permanent trapping.

| First internal exit | Launches |
| --- | ---: |
| Downward toward background plane | 278 |
| Upward toward unobserved scene | 265 |
| Lateral | 0 |
| None within cap | 6 |

Surface hemisphere and scene destination are different facts. Front means the upper ellipsoid hemisphere, not automatically an environment lookup.

| First exit hemisphere | Downward background | Upward environment |
| --- | ---: | ---: |
| Upper/front | 43 | 161 |
| Lower/back | 235 | 104 |

Across all later encounters, 1,940 transmitted branches become available. None has zero rounded total power in this run. All their endpoints remain recorded. Later repeated escapes and retained internal reflections are not collapsed into one selected exit.

## Conditional source support and scene roles

Every downward air branch intersects the fixed background plane before any infinite environment. Convexity and the actual outgoing branch exclude solid reentry. Plane intersections use original L and the corrected center, without border clamping. Every raw and incident-compatible four-corner mask check is retained separately.

Upward and lateral exits remain unobserved environment roles. Initial direct-front downward branches retain their background role rather than receiving annular black or white. No emitter is evaluated and no radiance is assigned anywhere in this audit.

The original known and radius-21 eroded-known arrays are hash-proven and reused under their original 43-by-43 support semantics. No new erosion or incident field runs. Reusing these map-independent support masks does not transfer an old primary-ray proof to new endpoints.

| Mean unit-launch power, this TIR cohort only | A raw | A incident-compatible | B raw | B incident-compatible |
| --- | ---: | ---: | ---: | ---: |
| Supported downward endpoints | 0.293479 | 0.274973 | 0.309888 | 0.299947 |
| Unsupported downward endpoints | 0.234712 | 0.253218 | 0.218304 | 0.228244 |
| Unknown environment | 0.454493 | 0.454493 | 0.454493 | 0.454493 |
| Geometrically unresolved events | 0 | 0 | 0 | 0 |
| Retained event-16 tail | 0.017315 | 0.017315 | 0.017315 | 0.017315 |

These are equal-launch interface-power partitions for the selected 549 rays, not whole-circle energy fractions, measured radiance or image errors. Incident compatibility is a separate mask diagnostic; it does not apply the transmission PSF or encoded tone to reflected light. Conditional temporal-mosaic availability remains different from photographic truth.

## The cap tail matters

The mean remaining tail is 1.73155 percent of unit launch power, while the largest individual tail is 83.36275 percent. Its complete separate s/p values remain in the indexed partition record. No tail receives a source color or is deleted because the cohort mean is smaller.

Unknown environment and unsupported downward endpoints would still prevent a complete scene even if that tail vanished. The current bounded audit therefore resolves actual continuation paths only through its declared encounter limit; it does not license a complete reflected image or a source completion.

## Evidence and accounting limits

| Record | Content |
| --- | --- |
| [Summary](summary.json) | Power partitions, first exits, event statuses and closure |
| [Ledger](ledger.json) | Persistent actual counters |
| [Decode reservation](decode-reservation.json) | Selected NPY shapes, dtypes and payload/header bounds |
| [Saved assessment](saved-assessment.json) | Hemisphere/scene distinctions and cached-vector checks |
| [Result](result.json) | Final status, all event summaries and clock |

Indexed event records preserve actual points, normals, directions, interface weights, discriminants, brackets, endpoints and availability. Initial events explicitly lack measured new brackets. Launch IDs map exactly to the original native cache. No hidden low-power culling or source-based reselection occurs.

The as-run extra `mask_header_bytes` ledger field is unused and remains zero. Selected NPY header sizes total 2,176 bytes per pass; validation and decoding each read them. Decoded mask containers and indexed lookups remain separate quantities; the payload counter includes every selected decoded member. This disclosure does not alter the executed ledger.

## Decision

Retain Search unchanged. The useful result is that the omitted rim paths have mixed background/environment exits and a non-small cap tail, rather than one absent outline mechanism. There is no new fidelity score, component adoption or historical pass count.

The next scientific rendering question was requested before packaging. A future complete image would need bounded continuation and supported scene radiance under explicit authority. No color, emitter, depth, source or geometry tuning follows automatically.
