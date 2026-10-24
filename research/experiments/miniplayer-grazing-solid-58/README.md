# Grazing normals reveal a different reflected-light role

One closed convex power solid creates grazing edge normals and downward direct reflection toward the frozen backdrop. Sparse reflectance rises from about four percent to ninety percent very near the rim. However, two-thirds of the primary probes undergo TIR, and four reflected endpoints lack modeled backdrop support. No full reconstruction or fidelity acceptance follows.

| Sparse physical test | Expanded | Compact |
| --- | ---: | ---: |
| Index-one complete comparators | 18 of 18 | 18 of 18 |
| Index 1.5 complete primary paths | 6 of 18 | 6 of 18 |
| Index 1.5 TIR/critical paths | 12 of 18 | 12 of 18 |
| Direct front reflections toward backdrop | 9 of 18 | 9 of 18 |

The [protocol](protocol.json) fixes one actual surface, index and source distance. It changes both physical face profiles coherently; it does not preserve the old inverse-designed correspondence or isolate a front-only effect. Original masks, sources, geometry evidence and public working family stay unchanged.

## Actual solid and convexity

Let rho be Euclidean distance to the inner rectangle, divided by the frozen corner radius. The level function is

$$
F(x,y,z)=\rho(x,y)^p+
\begin{cases}
\left(\frac{z}{H_{\rm front}}\right)^2,&z\ge0,\\
\left(\frac{z}{H_{\rm back}}\right)^2,&z<0
\end{cases}
-1.
$$

The front depth is 0.02 original length units. Back depth is the actual shallow41 center height. The exponent is the unchanged shallow41 value 33.76385521939009. These are inherited initialization assumptions, not measurements or a fit. Only major length differs between the family members.

Distance to the inner rectangle is convex. Its nonnegative power is convex and nondecreasing. The piecewise positive quadratic has matching zero derivative at its join and is convex. Their sum is convex; its unit sublevel is a closed convex solid.

The level gradient never vanishes on the surface. The implicit boundary is C1; the front graph has a vertical tangent at the projected equator.

The shared [implementation](../../../reconstruction/closed_power_surface.py) derives front roots, exit intersections, normals and sections from that same level function. It reuses the unchanged convex ordered intersector and Snell calculations. Analytic-gradient controls and the true-circle equal-height ellipsoid limit pass. No slope cap, independent normal, displacement patch or sampled-pixel warp is introduced.

[Same-surface section and rays](section-rays.svg) use retained arrays, physical axes at equal scale and no new geometric evaluation. [Paths and sections](paths-sections.npz) retain both indices, actual brackets, normals, primary statuses and direct-reflection directions.

## Why the light role changes

| Normalized radial coordinate | Front Fresnel reflectance | Direct reflection role |
| --- | ---: | --- |
| 0.99 | 0.04060 | Upward environment |
| 0.999 | 0.09295 | Downward backdrop |
| 0.9999 | 0.39358 | Downward backdrop |
| 0.999999 | 0.90506 | Downward backdrop |

These are ray powers, not pixel brightness. The highest values occur in extremely narrow subpixel bands. Positive geometric integration is therefore essential before any image claim. A grazing ray does not automatically see a white upper light: its reflected direction can point downward to the surrounding backdrop.

Across both references, 32 of 36 downward sparse endpoints have four-texel raw source support. Four remain unsupported; none is filled. Upward environment radiance is still unobserved. No source RGB is evaluated, so supported endpoints are not asserted white or uniquely responsible for the target rim.

The [source-role audit](source-role.json) is sparse and conditional, not a whole-body or finite-frosting proof. Specular backdrop support and frosted transmission support are separate roles. Existing primary source proofs do not transfer to this changed solid.

## Limit and next discriminating question

TIR is an actual path status, not a reason to replace normals or a complete rendering. Unresolved reflected/transmitted descendants retain their power. The sparse result motivates ordered branch transport with explicit backdrop/environment support; it does not justify painting a rim, raising scene intensity or treating blocked primary light as zero total light.

The [checkpoint](checkpoint.json), [result](result.json) and [ledger](ledger.json) preserve the original clock. Usage is 72 launches, 4841 level points and 101140 conservative adapter units. The fixture-level subset is 1645. There are 36 front Fresnel and reflection evaluations and 144 mask lookups, with zero RGB queries, full images or fits.
