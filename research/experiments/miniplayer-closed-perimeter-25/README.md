# Closed perimeter: valid geometry, grazing band unresolved by this grid

The same-footprint closed solid passes geometry and shared-tracer controls. All sampled transmitted primary endpoints have source support. The uniform grid misses most grazing front normals, however, so it cannot judge the missing bright perimeter. No RGB image, full-body source certificate or fidelity acceptance follows.

## One physical change

The [protocol](protocol.json) runs from 07:26:34.982 to 07:46:34.982 UTC. The [checkpoint](checkpoint.json) passed at 07:29:26.325. Radius, minor half-extent and original center front/back heights stay fixed. Both members change only major half-length.

A closed equator replaces the previous meeting of two finite-slope height graphs. The actual level, roots, normals, sections and internal segments all use one equation. Squared distance refers to the frozen inner rectangle.

$$
\begin{aligned}
F(x,y,z)&=\frac{d_{\mathrm{rectangle}}(x,y)^2}{R^2}+\left(\frac{z-z_c}{\eta}\right)^2-1,\\
z_c&=z_{\mathrm{front,center}}-\eta,\\
2\eta&=z_{\mathrm{front,center}}-z_{\mathrm{back,center}},\\
\boldsymbol n&=\frac{\nabla F}{\lVert\nabla F\rVert}.
\end{aligned}
$$

Squared distance to a convex rectangle is convex. Adding the positive vertical quadratic gives a convex solid globally for this fixed zero-coupling case. The surface is C1; second derivatives jump at footprint joins. Its equator is smooth, while a projected tangent remains an unresolved camera launch rather than a transmitted ray.

The [shared surface extension](../../../reconstruction/closed_crowned_surface.py) reuses the existing closed equation and ordered tracer. No normal correction, refraction warp, fitted silhouette, additional light or material is introduced. The frozen mask and selected models are not changed.

## Sampled transport

| Member | Sparse launches | Regular entry | Primary transmitted | TIR | Exact projected tangencies | Largest sampled front angle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Expanded | 2149 | 1909 | 1909 | 0 | 4 | 20.29 degrees |
| Compact | 2149 | 1885 | 1881 | 4 | 4 | 37.65 degrees |

All 3790 sampled completed primary paths pass radius-21 incident support and four bilinear corners in both references. That is 7580 source-role observations. TIR paths retain unavailable background coordinates. No replacement color or alternate path is fabricated.

Every sampled direct-front reflection points upward. This is a sampling result, not a theorem that the actual surface reflects only upward. The true grazing region contains downward first reflections that meet the background plane before any infinite environment.

## Why the grid is insufficient

For the uncoupled circular edge section, the front-normal angle obeys the following relation. It approaches ninety degrees at the equator.

$$
\tan\theta=\frac{\eta\rho}{R\sqrt{1-\rho^2}},\qquad
\rho_{45}=\frac{R}{\sqrt{R^2+\eta^2}}.
$$

The [derived edge-band width](edge-resolution.json) is approximately 0.22 native pixel for angles above forty-five degrees. The uniform 65-by-33 grid is too coarse to characterize it. Its observed angle maxima cannot support a positive or negative rim-light verdict.

A targeted native-perimeter study is therefore required. It must retain actual front power, distinguish downward background returns from unknown upward radiance, and audit source support before any reflected RGB. This record does not authorize source completion or discarding low-power or trapped paths.

## Inspect the actual geometry

| Member | Same-F sections and saved internal segments |
| --- | --- |
| Expanded | [SVG](expanded-actual-sections.svg) |
| Compact | [SVG](compact-actual-sections.svg) |

The diagrams use saved roots and actual entry/exit points. Vertical coordinates are magnified eight times and labeled; the source geometry is unchanged. [Presentation metadata](presentation.json) separates saved-array drawing from new optical calculations. These are geometric views, not reconstruction images.

## Work and decision

| Work | Actual |
| --- | ---: |
| True-circle fixture/comparator rays | 100 |
| Two sparse grids | 4298 rays |
| Primitive level points | 174555 |
| Conservative delegate units | 1146672 |
| First-front interface points | 3794 |
| Source-role mask observations | 7580 |
| Four-corner mask lookups | 30320 |
| Known-mask erosions | 4 |
| Actual section points | 2056 |
| RGB queries, optical filters, composites and fits | 0 |

A [pre-execution clarification](preflight-accounting.json) reserved both background endpoint roles; its initial declaration remains saved. Geometry and clock did not change. The [persistent ledger](ledger.json) and [result](result.json) retain actual counts and statuses.

Keep the solid as a mathematical candidate only. Its long straight body still has no longitudinal curvature; this test addresses the perimeter, not every refraction defect. Full native paths, secondary transport, source availability and scene radiance remain separate requirements before any complete optical rendering claim.
