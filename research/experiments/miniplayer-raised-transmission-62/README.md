# Raised-perimeter transmission fails the matched comparison

The existing shared annular height passes geometry and full source support, but its primary-transmission reconstruction fails all four matched aggregate comparisons. Returned text and bright bands land incorrectly; caps become dark or smeared. No blur, color, light or parameter fit rescues it. The public working model remains unchanged.

| Reference | Matched monotone E | Raised-perimeter E | Raised comparison |
| --- | ---: | ---: | --- |
| expanded A | 10.017110 | 33.889508 | [Image](expanded-a-raised-comparison.png) |
| expanded B | 8.198369 | 17.131426 | [Image](expanded-b-raised-comparison.png) |
| compact A | 24.136619 | 28.605752 | [Image](compact-a-raised-comparison.png) |
| compact B | 23.086012 | 25.647591 | [Image](compact-b-raised-comparison.png) |

All four raised comparisons were visually inspected. Expanded A develops a broad incorrect return and dark end-cap. Expanded B moves lettering without recovering the rim. Compact retains misplaced broad returns and dark caps. The [matched controls](result.json), [all scalar regressions](comparisons.json) and individual metrics retain partial, foreground, exterior and fixed-crop outcomes.

## One actual height law

The experiment imports the unchanged [raised-perimeter adapter](../../../reconstruction/raised_perimeter_back.py) and [annular scalar law](../../../reconstruction/annular_profile.py), already used for another control. It introduces no new shader, independent normal or source displacement. The scalar coordinate is the squared normalized distance of the frozen ordinary rounded footprint.

$$
h_1(t)=0.4(1-t)(0.1+t),\qquad
h_2(x)=0.4\left(1-\frac{x^2}{a^2}\right),\qquad
h=\frac{h_1h_2}{h_1+h_2}.
$$

The same height determines back position and derivatives. Harmonic composition retains nonnegative height and a global slope bound below the shared primary-path threshold. The solid can be nonconvex, so no convex multiple-reflection intersector is applied. Only major length differs between expanded and compact.

Both compared models have a flat front, index 1.5, background distance 2.1 original length units, incident sigma 6.75/radius 21, the same common working response, actual primary Fresnel throughput and zero added reflection illumination/shadow. Original foreground and every mask remain fixed. These are matched diagnostic nuisances, not an attempt to replay the public two-surface working image.

## Source-first validity

Frozen case/input hashes, unit-index identities and actual gradient controls pass before the [checkpoint](checkpoint.json). [Source proof](source-FIRST.json) covers both geometries, both lengths and both references before any changed filter or RGB query. Every whole-body and required original guard subray has complete finite-kernel/bilinear support. No undefined required sample, source extension or mask change occurs.

The [protocol](protocol.json) permits one prior and its matched control. Usage is 4486400 native rays plus 16 fixture rays, 8972912 charged height points and 179458240 conservative adapter units. Source audits cover 8972800 subrays and 71782400 mask lookups. Four incident fields, 8930800 RGB queries, eight composites and eight score calls remain within their original caps.

## Limits and decision

All raw encoded clipping counts are zero. Primary-only throughput retains back-reflected power as unassigned; it does not declare that light absent. The dark cap therefore cannot be attributed uniquely to source geometry or treated as full-radiance evidence. The [results](result.json) record the maximum retained back power.

AA2 is preserved for this matched structure diagnostic. Boundary convergence from the shallow-front experiment does not transfer to this changed refractive field. Complete native outputs, actual source coordinates/back normals and exact recipes are retained; full raw sample arrays are not archived. Conditional mosaic support remains distinct from photographic truth.

This rejects the rendered fixed prior as an improvement. It does not prove that all nonmonotone heights fail. A shorter physical background distance is a possible discriminating follow-up because propagation can be changed without altering the actual back normal or interface powers. No second distance or fit runs here.
