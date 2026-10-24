# Native first-front map: grazing reflection exists, scene support is incomplete

The full native lattice captures front incidence near ninety degrees and substantial local Fresnel reflectance. Many downward reflected endpoints remain outside the frozen source support, while upward radiance is unobserved. These are intrinsic first-interface power maps, not RGB reflections, complete scenes or fidelity improvements.

## Fixed scope and timing

The [protocol](protocol.json) starts at 07:49:33.231 and ends at 08:09:33.231 UTC. The first-member [checkpoint](checkpoint.json) passed at 07:50:38.966. Both original member lengths retain identical closed surface parameters; only major half-length changes.

Every front intersection and normal comes from the same [closed surface](../miniplayer-closed-perimeter-25/README.md). Shared reflection and Fresnel functions evaluate the initial interface only. No internal transport, source/target RGB decode, incident filter, fitted scene or color coefficient is evaluated.

## Native first-interface results

| Quantity | Expanded | Compact |
| --- | ---: | ---: |
| Regular front entries | 890848 | 596237 |
| Largest sampled front incidence | 89.408 degrees | 88.863 degrees |
| Front angles above 45 degrees | 4880 | 3292 |
| Front angles above 80 degrees | 2216 | 15 |
| Largest single-sample reflectance | 0.941954 | 0.891880 |
| Largest AA2 pixel mean reflectance | 0.338024 | 0.245185 |
| Downward reflected directions | 4880 | 3292 |
| Upward reflected directions | 885968 | 592945 |

The members use one cross-section. Their large sampled grazing-count difference is not evidence for different material. The native lattice has different measured pose phases and perimeter geometry. The [continuous-integration diagnostic](../miniplayer-grazing-quadrature-27/README.md) demonstrates severe AA2 error at one expanded straight-edge pixel.

| Member/reference | Downward endpoints | Raw source supported | Unsupported |
| --- | ---: | ---: | ---: |
| Expanded A | 4880 | 2281 | 2599 |
| Expanded B | 4880 | 2281 | 2599 |
| Compact A | 3292 | 174 | 3118 |
| Compact B | 3292 | 1578 | 1714 |

Downward rays intersect the original background plane before any infinite environment. Convexity and their outward normal derivative exclude solid reentry. Each endpoint checks all four raw-source bilinear corners. Reflection does not inherit transmission frosting or its encoded tone.

Upward radiance remains unknown. No annular black/white color is assigned here. All native samples, including unsupported endpoints and low-power events, remain in the retained arrays. Conditional source-mask availability is not photographic truth.

## Scalar maps

| Member | Unit first-front reflectance |
| --- | --- |
| Expanded | [Map](expanded-unit-reflectance.png) |
| Compact | [Map](compact-unit-reflectance.png) |

The display scale is linear from zero to one. The images show a coefficient under unit incoming radiance, not predicted scene brightness or an outline reconstruction. Pixel maps retain upward, supported-downward and unsupported-downward weights separately. They remain AA2 estimates rather than converged pixel integrals.

## Work and evidence

| Work | Actual |
| --- | ---: |
| Native first-front launches | 2243200 |
| Actual front level/normal points | 1487085 |
| Initial interface evaluations | 1487085 |
| Footprint points | 6729600 |
| Conservative delegate units | 49274965 |
| Background endpoint checks across both references | 16344 |
| Raw-mask corner lookups | 32200 |
| Source RGB queries, filters, fits and internal traces | 0 |

[First bindings](bindings-FIRST.json) and [last bindings](bindings-LAST.json) match for the known masks, cases, geometry and shared functions. The [result](result.json) and [ledger](ledger.json) retain actual categories. No original mask, source, selected model or scoring protocol changes.

The result explains why first-front reflection cannot be painted uniformly white. It also does not license an optical image from unsupported background texels. Numerical pixel integration, actual source support and unknown scene radiance remain independent requirements.
